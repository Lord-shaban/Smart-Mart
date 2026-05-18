# Smart Mart ERP & E-commerce System
## Full-Stack Database Systems — Academic Report

---

## 1. Introduction

Smart Mart is a comprehensive, production-grade Enterprise Resource Planning (ERP) and E-commerce platform designed for modern retail operations. It integrates a Point-of-Sale (POS) terminal, inventory management, customer loyalty program, and a digital storefront into a single unified system powered by a rigorously normalized relational database.

The system demonstrates advanced software engineering principles including RESTful API design, SQL-based collaborative filtering for product recommendations, demand forecasting through temporal analytics, and automated business logic via database triggers.

## 2. Problem Statement

Traditional retail businesses face significant challenges in managing inventory, processing sales, tracking customer loyalty, and predicting product demand. Many small-to-medium retailers rely on disconnected spreadsheets or fragmented systems that lead to:

- **Data Redundancy:** Customer and product information duplicated across systems.
- **Stock Mismanagement:** No real-time visibility into inventory levels or expiry dates.
- **Lost Revenue:** Inability to predict demand trends or identify near-expiry products for markdown.
- **Poor Customer Retention:** No loyalty tracking or personalized recommendations.

Smart Mart solves these problems through a fully integrated, database-driven platform.

## 3. Objectives

1. Design a normalized relational database schema (3NF) that eliminates redundancy and ensures data integrity.
2. Implement a complete RESTful API with full CRUD operations for all major entities.
3. Build a POS terminal for real-time barcode-based sales processing with stock validation.
4. Create a manager dashboard with analytics, demand forecasting, and expiry prediction.
5. Develop a digital storefront with category filtering, search, and cart functionality.
6. Implement a customer loyalty portal with SQL-based collaborative filtering recommendations.
7. Enforce business rules through database triggers and CHECK constraints.
8. Maintain an audit trail for all critical data mutations.

## 4. Entity-Relationship Diagram (ERD)

The system contains **9 tables** with well-defined relationships:

| Entity | Description | PK |
|---|---|---|
| CATEGORIES | Product classification lookup | category_id |
| SUPPLIERS | Vendor/supplier information | supplier_id |
| CUSTOMERS | Customer profiles & loyalty | customer_id |
| EMPLOYEES | Staff with role-based access | employee_id |
| PRODUCTS | Core inventory catalog | product_id |
| TRANSACTIONS | Sale event headers | transaction_id |
| TRANSACTION_ITEMS | Sale line items (bridge table) | (transaction_id, product_id) |
| EXPIRY_ALERTS | Product expiration tracking | alert_id |
| AUDIT_LOG | System event logging | log_id |

**Key Relationships:**
- CATEGORIES ←1:N→ PRODUCTS (one category has many products)
- SUPPLIERS ←1:N→ PRODUCTS (one supplier supplies many products)
- CUSTOMERS ←1:N→ TRANSACTIONS (one customer makes many transactions)
- EMPLOYEES ←1:N→ TRANSACTIONS (one employee processes many transactions)
- TRANSACTIONS ←1:N→ TRANSACTION_ITEMS ←N:1→ PRODUCTS (M:N resolved via bridge table)

*See `docs/ER_DIAGRAM.md` for the full Mermaid diagram.*

## 5. Database Normalization (1NF → 3NF)

### First Normal Form (1NF)
- ✅ All tables have a defined primary key
- ✅ All attributes contain atomic (indivisible) values
- ✅ No repeating groups or multi-valued attributes
- ✅ Each column has a unique name within its table

### Second Normal Form (2NF)
- ✅ All tables satisfy 1NF
- ✅ All non-key attributes are fully functionally dependent on the entire primary key
- ✅ The M:N relationship between PRODUCTS and TRANSACTIONS is resolved through the TRANSACTION_ITEMS bridge table with composite key (transaction_id, product_id)
- ✅ Category names were extracted into a separate CATEGORIES lookup table to eliminate partial dependencies

### Third Normal Form (3NF)
- ✅ All tables satisfy 2NF
- ✅ No transitive dependencies exist — all non-key attributes depend only on the primary key
- ✅ `member_tier` in CUSTOMERS is derived from `loyalty_points` but maintained via an automatic trigger (accepted denormalization for OLTP performance, enforced by `trg_update_member_tier`)
- ✅ `subtotal` in TRANSACTION_ITEMS is a materialized computed field (quantity × price_at_time) kept for historical immutability of financial records — a standard industry practice in ERP/POS systems
- ✅ `profit_margin_pct` is computed in a VIEW (not stored), preserving strict 3NF

## 6. Technologies Used

| Layer | Technology | Purpose |
|---|---|---|
| Backend | Python 3 + Flask | RESTful API server |
| Database | MySQL | Relational data storage |
| Frontend | HTML5, CSS3, Vanilla JS | User interface |
| UI Framework | Bootstrap 5 | Responsive grid & components |
| Icons | Font Awesome 6 | UI iconography |
| Architecture | MVC + REST | Separation of concerns |

## 7. SQL Implementation

### 7.1 Constraints
```sql
CHECK (price > 0)
CHECK (stock_quantity >= 0)
CHECK (loyalty_points >= 0)
CHECK (member_tier IN ('Bronze', 'Silver', 'Gold'))
CHECK (payment_method IN ('Cash', 'Card', 'Digital'))
CHECK (status IN ('Completed', 'Refunded', 'Voided'))
```

### 7.2 Foreign Keys with Referential Actions
```sql
FOREIGN KEY (category_id) REFERENCES CATEGORIES(category_id) ON DELETE SET NULL
FOREIGN KEY (supplier_id) REFERENCES SUPPLIERS(supplier_id)  ON DELETE SET NULL
FOREIGN KEY (employee_id) REFERENCES EMPLOYEES(employee_id)  ON DELETE RESTRICT
FOREIGN KEY (transaction_id) REFERENCES TRANSACTIONS(transaction_id) ON DELETE CASCADE
```

### 7.3 Views (6 total)
1. **v_product_details** — Full product info with JOINed category & supplier names
2. **v_daily_sales** — Aggregated daily revenue with GROUP BY
3. **v_inventory_status** — Stock health with CASE expressions
4. **v_customer_lifetime** — Customer lifetime value analytics
5. **v_employee_performance** — Employee transaction metrics
6. **v_category_revenue** — Revenue breakdown by category

### 7.4 Triggers (6 total)
1. **trg_update_member_tier** — Auto-updates customer loyalty tier
2. **trg_expiry_alert_on_insert** — Creates alert for near-expiry products on insertion
3. **trg_audit_new_transaction** — Logs all new transactions
4. **trg_audit_product_price_change** — Tracks price modifications
5. **trg_product_updated_at** — Maintains updated_at timestamp
6. **trg_expiry_alert_on_update** — Monitors expiry date changes

### 7.5 Indexes (19 total)
Performance-optimized covering indexes on all foreign keys, frequently queried columns, and composite search patterns.

### 7.6 Advanced Queries
- **Collaborative Filtering:** Pure SQL recommendation engine using correlated subqueries
- **Demand Forecasting:** Week-over-week comparison using conditional aggregation (CASE + SUM)
- **Expiry Prediction:** Date arithmetic for proactive markdown suggestions

## 8. Backend Explanation

### Architecture
Single-module Flask application following MVC pattern:
- **Model Layer:** SQLite3 with parameterized queries (SQL injection safe)
- **Controller Layer:** RESTful API endpoints with proper HTTP verbs
- **View Layer:** Server-rendered Jinja2 templates

### API Endpoints (25+)
| Method | Endpoint | Description |
|---|---|---|
| GET | /api/products | List all active products |
| POST | /api/products | Create new product |
| PUT | /api/products/:id | Update product |
| DELETE | /api/products/:id | Soft-delete product |
| GET | /api/customers | List customers with lifetime stats |
| POST | /api/customers | Register customer |
| PUT | /api/customers/:id | Update customer |
| DELETE | /api/customers/:id | Remove customer |
| GET | /api/employees | List active employees |
| POST | /api/employees | Add employee |
| PUT | /api/employees/:id | Update employee |
| DELETE | /api/employees/:id | Soft-delete employee |
| GET/POST | /api/suppliers | List/Create suppliers |
| PUT/DELETE | /api/suppliers/:id | Update/Delete suppliers |
| POST | /api/transactions | Process sale |
| GET | /api/transactions/recent | Recent transactions |
| GET | /api/manager/reports | Dashboard analytics |
| POST | /api/manager/apply-discount/:id | Apply expiry discount |
| GET | /api/audit-log | View audit trail |
| GET | /api/dashboard/stats | Quick statistics |

### Security Measures
- Parameterized queries (`?` placeholders) prevent SQL injection
- Input validation on all POST/PUT endpoints
- Proper HTTP status codes (200, 201, 400, 404, 500)
- Soft-delete pattern preserves referential integrity
- Request-scoped database connections with automatic cleanup

## 9. Frontend Explanation

### 4 Distinct Interfaces

1. **Landing Page (`/`)** — System overview with navigation cards and tech stack badges
2. **POS Terminal (`/cashier`)** — Barcode scanning, cart management, customer lookup, receipt printing
3. **Manager Dashboard (`/manager`)** — KPI stat cards, top products, low stock alerts, expiry predictor, demand forecaster
4. **Online Store (`/store`)** — Product catalog with category filtering, search, cart sidebar, checkout
5. **Customer Portal (`/customer`)** — Loyalty profile, purchase history, AI recommendations

### Design Principles
- Premium glassmorphism design language
- Responsive layout (Bootstrap 5 grid)
- Real-time data fetching via Fetch API
- Toast notifications for user feedback
- Print-ready receipt generation
- localStorage for session persistence

## 10. Testing

### Constraint Testing
- CHECK constraints validated: negative prices, invalid roles, invalid payment methods all rejected
- UNIQUE constraints tested: duplicate barcodes, phones, emails rejected
- FK constraints tested: CASCADE, SET NULL, RESTRICT behaviors verified

### Integration Testing
- Seed script (`seed.py`) generates 45 products, 100 customers, 4 employees, 1200 transactions
- All API endpoints tested via browser and Fetch API
- Transaction processing validates stock availability before deduction

### System Testing
- Cross-module flow: Store → Cart → Checkout → Customer Portal (points reflected)
- POS → Manager Dashboard (sales reflected in analytics)
- Expiry discount applied → Price updated → Audit log recorded

## 11. Challenges & Solutions

| Challenge | Solution |
|---|---|
| AI recommendations without ML libraries | Pure SQL collaborative filtering using correlated subqueries |
| Maintaining 3NF with computed fields | Used VIEWs for derived data; documented accepted denormalizations |
| Historical price immutability | `price_at_time` field in TRANSACTION_ITEMS captures sale-time price |
| Real-time stock validation | Transaction API validates and deducts atomically with rollback |
| Audit trail without performance impact | Lightweight trigger-based logging |

## 12. Future Improvements

1. **Authentication & Authorization:** JWT-based auth with role-based access control
2. **Barcode Scanner Integration:** WebRTC camera-based barcode scanning
3. **Advanced Analytics:** Chart.js/D3.js visualizations for sales trends
4. **Inventory Forecasting:** Machine learning-based demand prediction
5. **Multi-store Support:** Store entity for chain management
6. **Email Notifications:** Automated low-stock and expiry alerts
7. **Mobile Responsive PWA:** Progressive Web App for mobile POS
8. **Database Migration:** PostgreSQL for production scalability

## 13. Conclusion

The Smart Mart ERP system demonstrates a complete, production-quality full-stack application built on rigorous database design principles. The 9-table schema in Third Normal Form, combined with 6 views, 6 triggers, 19 indexes, and comprehensive CHECK/FK constraints, showcases deep understanding of relational database theory and practical implementation.

The RESTful API provides complete CRUD operations across all entities with proper validation, error handling, and security measures. The four distinct frontend interfaces demonstrate real-world application of database-driven web development, from POS transactions to AI-powered recommendations using pure SQL.

This project bridges academic database theory with professional software engineering practices, resulting in a system that is both pedagogically demonstrative and functionally production-ready.
