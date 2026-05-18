# Smart Mart ERP & E-commerce System

## Entity-Relationship Diagram (ERD)

### Relationship Summary

| Relationship | Cardinality | Description |
|---|---|---|
| CATEGORIES → PRODUCTS | 1:N | One category has many products |
| SUPPLIERS → PRODUCTS | 1:N | One supplier supplies many products |
| CUSTOMERS → TRANSACTIONS | 1:N | One customer makes many transactions |
| EMPLOYEES → TRANSACTIONS | 1:N | One employee processes many transactions |
| TRANSACTIONS → TRANSACTION_ITEMS | 1:N | One transaction contains many line items |
| PRODUCTS → TRANSACTION_ITEMS | 1:N | One product appears in many line items |
| PRODUCTS → EXPIRY_ALERTS | 1:N | One product can have many expiry alerts |

### Mermaid ERD

```mermaid
erDiagram
    CATEGORIES ||--o{ PRODUCTS : "has"
    SUPPLIERS ||--o{ PRODUCTS : "supplies"
    PRODUCTS ||--o{ TRANSACTION_ITEMS : "included_in"
    PRODUCTS ||--o{ EXPIRY_ALERTS : "triggers"
    TRANSACTIONS ||--o{ TRANSACTION_ITEMS : "contains"
    CUSTOMERS ||--o{ TRANSACTIONS : "makes"
    EMPLOYEES ||--o{ TRANSACTIONS : "processes"
    EMPLOYEES ||--o{ EXPIRY_ALERTS : "resolves"

    CATEGORIES {
        int category_id PK
        string name UK
        string icon
        text description
        boolean is_active
        datetime created_at
    }

    SUPPLIERS {
        int supplier_id PK
        string name
        string contact_person
        string phone
        string email
        text address
        boolean is_active
        datetime created_at
    }

    CUSTOMERS {
        int customer_id PK
        string name
        string phone UK
        string email UK
        int loyalty_points
        date join_date
        string member_tier
        boolean is_active
    }

    EMPLOYEES {
        int employee_id PK
        string name
        string role
        string shift
        date hire_date
        date birth_date
        string phone
        boolean is_active
    }

    PRODUCTS {
        int product_id PK
        string barcode UK
        string name
        int category_id FK
        decimal price
        decimal cost_price
        int stock_quantity
        date expiry_date
        int supplier_id FK
        int reorder_level
        boolean is_active
        datetime created_at
        datetime updated_at
    }

    TRANSACTIONS {
        int transaction_id PK
        datetime date_time
        int customer_id FK
        int employee_id FK
        decimal total_amount
        string payment_method
        int loyalty_points_earned
        string status
    }

    TRANSACTION_ITEMS {
        int transaction_id PK_FK
        int product_id PK_FK
        int quantity
        decimal price_at_time
        decimal subtotal
    }

    EXPIRY_ALERTS {
        int alert_id PK
        int product_id FK
        date alert_date
        string status
        decimal discount_applied
        int resolved_by FK
        datetime resolved_at
    }

    AUDIT_LOG {
        int log_id PK
        string table_name
        string action
        int record_id
        text old_values
        text new_values
        text details
        int performed_by
        datetime performed_at
    }
```

### Design Notes

- **9 tables** in Third Normal Form (3NF)
- **TRANSACTION_ITEMS** is a junction/bridge table resolving the M:N relationship between TRANSACTIONS and PRODUCTS
- **AUDIT_LOG** is a standalone event-sourcing table (no FK constraints to allow logging deleted records)
- **Composite Primary Key** on TRANSACTION_ITEMS (transaction_id, product_id)
- All tables use `AUTOINCREMENT` surrogate keys except the junction table
- Referential integrity enforced via `ON DELETE CASCADE`, `SET NULL`, and `RESTRICT`
