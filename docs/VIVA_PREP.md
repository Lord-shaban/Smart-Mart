# Smart Mart — Viva/Presentation Preparation

## Likely Questions & Strong Answers

### Q1: Why did you choose MySQL over SQLite/PostgreSQL?
**A:** MySQL (InnoDB) was chosen to support a server-based deployment with stronger concurrency, transactions, and production features (replication, backup tools, tuning). It provides better write concurrency and scalable connections for multi-user POS environments. The schema remains portable to other RDBMS with minor changes.

### Q2: Explain your normalization process to 3NF.
**A:** 
- **1NF:** Every table has a primary key, all values are atomic, no repeating groups.
- **2NF:** We extracted categories into a separate lookup table to eliminate partial dependencies. The TRANSACTION_ITEMS bridge table resolves the M:N relationship with a composite key.
- **3NF:** No transitive dependencies. `member_tier` is derived from `loyalty_points` but maintained via trigger for query performance — a documented, accepted denormalization. `subtotal` in TRANSACTION_ITEMS is kept for historical immutability, standard in financial systems.

### Q3: How does your collaborative filtering recommendation work?
**A:** It's pure SQL using correlated subqueries:
1. Find products the current customer has purchased
2. Find other customers who bought those same products
3. Find products those similar customers bought that the current customer hasn't
4. Rank by frequency (score) and return top 5
This implements User-Based Collaborative Filtering without any ML framework.

### Q4: How do you prevent SQL injection?
**A:** All database queries use parameterized placeholders (`?`). We never concatenate user input into SQL strings. Flask's `request.json` parsing combined with our `validate_required()` helper ensures data integrity before it reaches the database layer.

### Q5: What are your triggers and why?
**A:** We have 6 triggers:
1. `trg_update_member_tier` — Automatically promotes/demotes loyalty tier when points change
2. `trg_expiry_alert_on_insert` — Creates alerts for near-expiry products on insertion
3. `trg_audit_new_transaction` — Logs every sale for audit trail
4. `trg_audit_product_price_change` — Tracks price modifications with old/new values
5. `trg_product_updated_at` — Maintains modification timestamp
6. `trg_expiry_alert_on_update` — Monitors expiry date changes

### Q6: Explain the bridge table TRANSACTION_ITEMS.
**A:** TRANSACTIONS and PRODUCTS have a many-to-many relationship — one transaction can include multiple products, and one product can appear in multiple transactions. TRANSACTION_ITEMS resolves this with a composite primary key (transaction_id, product_id). It also stores `price_at_time` to preserve the historical sale price even if the product price changes later.

### Q7: What is soft-delete and why use it?
**A:** Instead of physically deleting records with DELETE, we set `is_active = 0`. This preserves referential integrity — if we deleted an employee, all their transaction records would break. Soft-delete keeps historical data intact while hiding deactivated records from active queries.

### Q8: How does your demand forecasting work?
**A:** We compare the last 7 days of sales against the previous 7 days using conditional aggregation:
```sql
SUM(CASE WHEN date >= last_7_days THEN quantity ELSE 0 END) AS recent
SUM(CASE WHEN date >= last_14_days AND date < last_7_days THEN quantity ELSE 0 END) AS previous
```
Products where recent > previous are flagged as trending upward.

### Q9: What are your views and why not just write the queries directly?
**A:** Views provide reusable query abstractions. `v_product_details` joins 3 tables — writing that JOIN every time would be error-prone and violate DRY. Views also encapsulate complex business logic (like stock status classification) in one place, making the API layer cleaner.

### Q10: How do you handle concurrent stock issues?
**A:** The transaction API validates stock availability, deducts quantities, and commits atomically. If any item fails validation, we call `db.rollback()` to revert all changes. SQLite's WAL journal mode provides safe concurrent reads during writes.

### Q11: What is the AUDIT_LOG table for?
**A:** It provides a complete audit trail of all data mutations. Triggers automatically log INSERT, UPDATE, and DELETE operations with timestamps, old/new values, and the performing user. This is essential for compliance, debugging, and accountability in any production system.

### Q12: Why 19 indexes? Isn't that too many?
**A:** Each index targets a specific, frequent query pattern. Foreign key columns need indexes for JOIN performance. We index `barcode` for POS lookups, `date_time` for reporting queries, `phone` for customer search, and `status` fields for filtered queries. The write overhead is negligible for our transaction volume.
