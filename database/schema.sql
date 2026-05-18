-- ============================================================
-- Smart Mart ERP & E-commerce System
-- Database Schema Definition (MySQL 8.0)
-- Normalization Level: Third Normal Form (3NF)
-- Version: 2.0 — Production-Ready Academic Schema
-- ============================================================

SET FOREIGN_KEY_CHECKS = 1;

-- ============================================================
-- 1. CATEGORIES (Lookup / Reference Table)
-- ============================================================
CREATE TABLE IF NOT EXISTS CATEGORIES (
    category_id   INT AUTO_INCREMENT PRIMARY KEY,
    name          VARCHAR(100) NOT NULL UNIQUE,
    icon          VARCHAR(50)  DEFAULT 'fa-box',
    description   TEXT,
    is_active     BOOLEAN DEFAULT TRUE,
    created_at    DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================================
-- 2. SUPPLIERS
-- ============================================================
CREATE TABLE IF NOT EXISTS SUPPLIERS (
    supplier_id    INT AUTO_INCREMENT PRIMARY KEY,
    name           VARCHAR(255) NOT NULL,
    contact_person VARCHAR(255),
    phone          VARCHAR(50),
    email          VARCHAR(255),
    address        TEXT,
    is_active      BOOLEAN DEFAULT TRUE,
    created_at     DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================================
-- 3. CUSTOMERS
-- ============================================================
CREATE TABLE IF NOT EXISTS CUSTOMERS (
    customer_id    INT AUTO_INCREMENT PRIMARY KEY,
    name           VARCHAR(255) NOT NULL,
    phone          VARCHAR(50)  UNIQUE,
    email          VARCHAR(255) UNIQUE,
    loyalty_points INT DEFAULT 0 CHECK (loyalty_points >= 0),
    join_date      DATE DEFAULT (CURDATE()),
    member_tier    VARCHAR(20) DEFAULT 'Bronze'
                   CHECK (member_tier IN ('Bronze', 'Silver', 'Gold')),
    is_active      BOOLEAN DEFAULT TRUE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================================
-- 4. EMPLOYEES
-- ============================================================
CREATE TABLE IF NOT EXISTS EMPLOYEES (
    employee_id   INT AUTO_INCREMENT PRIMARY KEY,
    name          VARCHAR(255) NOT NULL,
    role          VARCHAR(50) CHECK (role IN ('Cashier', 'Manager', 'Admin')),
    shift         VARCHAR(50) CHECK (shift IN ('Day', 'Night', 'Rotating')),
    hire_date     DATE DEFAULT (CURDATE()),
    birth_date    DATE,
    phone         VARCHAR(50),
    is_active     BOOLEAN DEFAULT TRUE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================================
-- 5. PRODUCTS
-- ============================================================
CREATE TABLE IF NOT EXISTS PRODUCTS (
    product_id     INT AUTO_INCREMENT PRIMARY KEY,
    barcode        VARCHAR(100) UNIQUE NOT NULL,
    name           VARCHAR(255) NOT NULL,
    category_id    INT,
    price          DECIMAL(10, 2) NOT NULL CHECK (price > 0),
    cost_price     DECIMAL(10, 2) CHECK (cost_price >= 0),
    stock_quantity INT NOT NULL DEFAULT 0 CHECK (stock_quantity >= 0),
    expiry_date    DATE,
    supplier_id    INT,
    reorder_level  INT DEFAULT 10,
    is_active      BOOLEAN DEFAULT TRUE,
    created_at     DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at     DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES CATEGORIES(category_id) ON DELETE SET NULL,
    FOREIGN KEY (supplier_id) REFERENCES SUPPLIERS(supplier_id)  ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================================
-- 6. TRANSACTIONS
-- ============================================================
CREATE TABLE IF NOT EXISTS TRANSACTIONS (
    transaction_id        INT AUTO_INCREMENT PRIMARY KEY,
    date_time             DATETIME DEFAULT CURRENT_TIMESTAMP,
    customer_id           INT,
    employee_id           INT NOT NULL,
    total_amount          DECIMAL(10, 2) NOT NULL DEFAULT 0
                          CHECK (total_amount >= 0),
    payment_method        VARCHAR(50)
                          CHECK (payment_method IN ('Cash', 'Card', 'Digital')),
    loyalty_points_earned INT DEFAULT 0,
    status                VARCHAR(20) DEFAULT 'Completed'
                          CHECK (status IN ('Completed', 'Refunded', 'Voided')),
    FOREIGN KEY (customer_id) REFERENCES CUSTOMERS(customer_id) ON DELETE SET NULL,
    FOREIGN KEY (employee_id) REFERENCES EMPLOYEES(employee_id) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================================
-- 7. TRANSACTION_ITEMS (Junction / Bridge Table)
-- ============================================================
CREATE TABLE IF NOT EXISTS TRANSACTION_ITEMS (
    transaction_id  INT NOT NULL,
    product_id      INT NOT NULL,
    quantity        INT NOT NULL CHECK (quantity > 0),
    price_at_time   DECIMAL(10, 2) NOT NULL CHECK (price_at_time >= 0),
    subtotal        DECIMAL(10, 2) NOT NULL CHECK (subtotal >= 0),
    PRIMARY KEY (transaction_id, product_id),
    FOREIGN KEY (transaction_id) REFERENCES TRANSACTIONS(transaction_id) ON DELETE CASCADE,
    FOREIGN KEY (product_id)     REFERENCES PRODUCTS(product_id)         ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================================
-- 8. EXPIRY_ALERTS
-- ============================================================
CREATE TABLE IF NOT EXISTS EXPIRY_ALERTS (
    alert_id          INT AUTO_INCREMENT PRIMARY KEY,
    product_id        INT NOT NULL,
    alert_date        DATE DEFAULT (CURDATE()),
    status            VARCHAR(50) DEFAULT 'Active'
                      CHECK (status IN ('Active', 'Resolved', 'Dismissed')),
    discount_applied  DECIMAL(5, 2) DEFAULT 0
                      CHECK (discount_applied >= 0 AND discount_applied <= 100),
    resolved_by       INT,
    resolved_at       DATETIME,
    FOREIGN KEY (product_id)  REFERENCES PRODUCTS(product_id)   ON DELETE CASCADE,
    FOREIGN KEY (resolved_by) REFERENCES EMPLOYEES(employee_id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================================
-- 9. AUDIT_LOG (System Event Tracking)
-- ============================================================
CREATE TABLE IF NOT EXISTS AUDIT_LOG (
    log_id        INT AUTO_INCREMENT PRIMARY KEY,
    table_name    VARCHAR(100) NOT NULL,
    action        VARCHAR(20)  NOT NULL
                  CHECK (action IN ('INSERT', 'UPDATE', 'DELETE')),
    record_id     INT,
    old_values    TEXT,
    new_values    TEXT,
    details       TEXT,
    performed_by  INT,
    performed_at  DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


-- ============================================================
-- INDEXES
-- ============================================================
CREATE INDEX idx_products_category   ON PRODUCTS(category_id);
CREATE INDEX idx_products_supplier   ON PRODUCTS(supplier_id);
CREATE INDEX idx_products_expiry     ON PRODUCTS(expiry_date);
CREATE INDEX idx_products_active     ON PRODUCTS(is_active);
CREATE INDEX idx_products_name       ON PRODUCTS(name);
CREATE INDEX idx_transactions_cust   ON TRANSACTIONS(customer_id);
CREATE INDEX idx_transactions_emp    ON TRANSACTIONS(employee_id);
CREATE INDEX idx_transactions_date   ON TRANSACTIONS(date_time);
CREATE INDEX idx_transactions_status ON TRANSACTIONS(status);
CREATE INDEX idx_tx_items_product    ON TRANSACTION_ITEMS(product_id);
CREATE INDEX idx_customers_active    ON CUSTOMERS(is_active);
CREATE INDEX idx_expiry_status       ON EXPIRY_ALERTS(status);
CREATE INDEX idx_expiry_product      ON EXPIRY_ALERTS(product_id);
CREATE INDEX idx_audit_table         ON AUDIT_LOG(table_name);
CREATE INDEX idx_audit_action        ON AUDIT_LOG(action);
CREATE INDEX idx_audit_timestamp     ON AUDIT_LOG(performed_at);


-- ============================================================
-- VIEWS
-- ============================================================

-- View 1: Full product details
CREATE OR REPLACE VIEW v_product_details AS
SELECT
    p.product_id, p.barcode, p.name,
    c.name       AS category,
    c.icon       AS category_icon,
    p.price, p.cost_price,
    p.stock_quantity, p.reorder_level,
    p.expiry_date, p.is_active,
    p.category_id, p.supplier_id,
    s.name       AS supplier_name,
    ROUND(((p.price - IFNULL(p.cost_price, 0)) / p.price) * 100, 1) AS profit_margin_pct,
    CASE
        WHEN p.stock_quantity <= p.reorder_level     THEN 'LOW'
        WHEN p.stock_quantity <= p.reorder_level * 2 THEN 'MEDIUM'
        ELSE 'OK'
    END AS stock_status
FROM PRODUCTS p
LEFT JOIN CATEGORIES c ON p.category_id = c.category_id
LEFT JOIN SUPPLIERS  s ON p.supplier_id  = s.supplier_id;

-- View 2: Daily sales summary
CREATE OR REPLACE VIEW v_daily_sales AS
SELECT
    DATE(t.date_time)                    AS sale_date,
    COUNT(DISTINCT t.transaction_id)     AS num_transactions,
    ROUND(SUM(t.total_amount), 2)        AS total_revenue,
    SUM(t.loyalty_points_earned)         AS total_points_issued,
    ROUND(AVG(t.total_amount), 2)        AS avg_transaction_value
FROM TRANSACTIONS t
WHERE t.status = 'Completed'
GROUP BY DATE(t.date_time)
ORDER BY sale_date DESC;

-- View 3: Inventory health status
CREATE OR REPLACE VIEW v_inventory_status AS
SELECT
    p.product_id, p.name, p.barcode,
    c.name AS category,
    p.stock_quantity, p.reorder_level, p.expiry_date,
    s.name AS supplier_name,
    CASE
        WHEN p.stock_quantity = 0                    THEN 'OUT_OF_STOCK'
        WHEN p.stock_quantity <= p.reorder_level     THEN 'LOW'
        WHEN p.stock_quantity <= p.reorder_level * 2 THEN 'MEDIUM'
        ELSE 'OK'
    END AS stock_status,
    CASE
        WHEN p.expiry_date IS NULL                                     THEN 'N/A'
        WHEN p.expiry_date <= CURDATE()                                THEN 'EXPIRED'
        WHEN p.expiry_date <= DATE_ADD(CURDATE(), INTERVAL 7 DAY)      THEN 'EXPIRING_SOON'
        WHEN p.expiry_date <= DATE_ADD(CURDATE(), INTERVAL 30 DAY)     THEN 'EXPIRING_MONTH'
        ELSE 'OK'
    END AS expiry_status
FROM PRODUCTS p
LEFT JOIN CATEGORIES c ON p.category_id = c.category_id
LEFT JOIN SUPPLIERS  s ON p.supplier_id  = s.supplier_id
WHERE p.is_active = 1;

-- View 4: Customer lifetime value
CREATE OR REPLACE VIEW v_customer_lifetime AS
SELECT
    c.customer_id, c.name, c.phone, c.email,
    c.member_tier, c.loyalty_points, c.join_date, c.is_active,
    COUNT(DISTINCT t.transaction_id)         AS total_orders,
    IFNULL(ROUND(SUM(t.total_amount), 2), 0) AS lifetime_spending,
    IFNULL(ROUND(AVG(t.total_amount), 2), 0) AS avg_order_value,
    MAX(t.date_time)                         AS last_purchase
FROM CUSTOMERS c
LEFT JOIN TRANSACTIONS t ON c.customer_id = t.customer_id
    AND t.status = 'Completed'
GROUP BY c.customer_id;

-- View 5: Employee performance
CREATE OR REPLACE VIEW v_employee_performance AS
SELECT
    e.employee_id, e.name, e.role, e.shift,
    COUNT(DISTINCT t.transaction_id)          AS total_transactions,
    IFNULL(ROUND(SUM(t.total_amount), 2), 0) AS total_revenue,
    IFNULL(ROUND(AVG(t.total_amount), 2), 0) AS avg_transaction_value,
    MAX(t.date_time)                         AS last_transaction
FROM EMPLOYEES e
LEFT JOIN TRANSACTIONS t ON e.employee_id = t.employee_id
    AND t.status = 'Completed'
WHERE e.is_active = 1
GROUP BY e.employee_id;

-- View 6: Revenue by category
CREATE OR REPLACE VIEW v_category_revenue AS
SELECT
    c.category_id, c.name AS category_name, c.icon,
    COUNT(DISTINCT ti.transaction_id) AS total_orders,
    SUM(ti.quantity)                   AS units_sold,
    ROUND(SUM(ti.subtotal), 2)         AS total_revenue,
    ROUND(AVG(ti.subtotal), 2)         AS avg_item_revenue
FROM CATEGORIES c
LEFT JOIN PRODUCTS p ON c.category_id = p.category_id
LEFT JOIN TRANSACTION_ITEMS ti ON p.product_id = ti.product_id
LEFT JOIN TRANSACTIONS t ON ti.transaction_id = t.transaction_id
    AND t.status = 'Completed'
GROUP BY c.category_id
ORDER BY total_revenue DESC;


-- ============================================================
-- TRIGGERS
-- ============================================================

-- Trigger 1: Auto-update customer tier
DELIMITER //
CREATE TRIGGER trg_update_member_tier
AFTER UPDATE ON CUSTOMERS
FOR EACH ROW
BEGIN
    IF NEW.loyalty_points != OLD.loyalty_points THEN
        UPDATE CUSTOMERS SET member_tier =
            CASE
                WHEN NEW.loyalty_points >= 1000 THEN 'Gold'
                WHEN NEW.loyalty_points >= 500  THEN 'Silver'
                ELSE 'Bronze'
            END
        WHERE customer_id = NEW.customer_id;
    END IF;
END //

-- Trigger 2: Expiry alert on product insert
CREATE TRIGGER trg_expiry_alert_on_insert
AFTER INSERT ON PRODUCTS
FOR EACH ROW
BEGIN
    IF NEW.expiry_date IS NOT NULL
       AND NEW.expiry_date <= DATE_ADD(CURDATE(), INTERVAL 7 DAY)
       AND NEW.expiry_date >= CURDATE()
    THEN
        INSERT INTO EXPIRY_ALERTS (product_id, status)
        VALUES (NEW.product_id, 'Active');
    END IF;
END //

-- Trigger 3: Audit new transaction
CREATE TRIGGER trg_audit_new_transaction
AFTER INSERT ON TRANSACTIONS
FOR EACH ROW
BEGIN
    INSERT INTO AUDIT_LOG (table_name, action, record_id, details, performed_by)
    VALUES (
        'TRANSACTIONS', 'INSERT', NEW.transaction_id,
        CONCAT('amount=', NEW.total_amount, ' method=', IFNULL(NEW.payment_method, 'N/A')),
        NEW.employee_id
    );
END //

-- Trigger 4: Audit product price changes
CREATE TRIGGER trg_audit_product_price_change
BEFORE UPDATE ON PRODUCTS
FOR EACH ROW
BEGIN
    IF OLD.price != NEW.price THEN
        INSERT INTO AUDIT_LOG (table_name, action, record_id, old_values, new_values, details)
        VALUES (
            'PRODUCTS', 'UPDATE', NEW.product_id,
            CONCAT('price=', OLD.price),
            CONCAT('price=', NEW.price),
            CONCAT('Price changed from $', OLD.price, ' to $', NEW.price)
        );
    END IF;
END //

-- Trigger 5: Expiry alert on product update
CREATE TRIGGER trg_expiry_alert_on_update
AFTER UPDATE ON PRODUCTS
FOR EACH ROW
BEGIN
    IF NEW.expiry_date IS NOT NULL
       AND NEW.expiry_date <= DATE_ADD(CURDATE(), INTERVAL 7 DAY)
       AND NEW.expiry_date >= CURDATE()
       AND NOT EXISTS (
           SELECT 1 FROM EXPIRY_ALERTS
           WHERE product_id = NEW.product_id AND status = 'Active'
       )
    THEN
        INSERT INTO EXPIRY_ALERTS (product_id, status)
        VALUES (NEW.product_id, 'Active');
    END IF;
END //

DELIMITER ;
