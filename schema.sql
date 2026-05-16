CREATE TABLE SUPPLIERS (
    supplier_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(255) NOT NULL,
    contact_person VARCHAR(255),
    phone VARCHAR(50),
    email VARCHAR(255)
);

CREATE TABLE CUSTOMERS (
    customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(255) NOT NULL,
    phone VARCHAR(50) UNIQUE,
    email VARCHAR(255) UNIQUE,
    loyalty_points INTEGER DEFAULT 0 CHECK (loyalty_points >= 0),
    join_date DATE DEFAULT (DATE('now')),
    member_tier VARCHAR(20) DEFAULT 'Bronze' CHECK (member_tier IN ('Bronze', 'Silver', 'Gold'))
);

CREATE TABLE EMPLOYEES (
    employee_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(255) NOT NULL,
    role VARCHAR(50) CHECK (role IN ('Cashier', 'Manager')),
    shift VARCHAR(50),
    hire_date DATE DEFAULT (DATE('now')),
    birth_date DATE
);

CREATE TABLE PRODUCTS (
    product_id INTEGER PRIMARY KEY AUTOINCREMENT,
    barcode VARCHAR(100) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    category VARCHAR(100),
    price DECIMAL(10, 2) NOT NULL CHECK (price > 0),
    cost_price DECIMAL(10, 2),
    stock_quantity INTEGER NOT NULL DEFAULT 0 CHECK (stock_quantity >= 0),
    expiry_date DATE,
    supplier_id INTEGER,
    reorder_level INTEGER DEFAULT 10,
    FOREIGN KEY (supplier_id) REFERENCES SUPPLIERS(supplier_id)
);

CREATE TABLE TRANSACTIONS (
    transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
    date_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    customer_id INTEGER,
    employee_id INTEGER NOT NULL,
    total_amount DECIMAL(10, 2) NOT NULL CHECK (total_amount >= 0),
    payment_method VARCHAR(50) CHECK (payment_method IN ('Cash', 'Card', 'Digital')),
    loyalty_points_earned INTEGER DEFAULT 0,
    FOREIGN KEY (customer_id) REFERENCES CUSTOMERS(customer_id),
    FOREIGN KEY (employee_id) REFERENCES EMPLOYEES(employee_id)
);

CREATE TABLE TRANSACTION_ITEMS (
    transaction_id INTEGER,
    product_id INTEGER,
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    price_at_time DECIMAL(10, 2) NOT NULL,
    subtotal DECIMAL(10, 2) NOT NULL,
    PRIMARY KEY (transaction_id, product_id),
    FOREIGN KEY (transaction_id) REFERENCES TRANSACTIONS(transaction_id),
    FOREIGN KEY (product_id) REFERENCES PRODUCTS(product_id)
);

CREATE TABLE EXPIRY_ALERTS (
    alert_id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER,
    alert_date DATE DEFAULT (DATE('now')),
    status VARCHAR(50) DEFAULT 'Active' CHECK (status IN ('Active', 'Resolved')),
    discount_applied DECIMAL(5, 2) DEFAULT 0,
    FOREIGN KEY (product_id) REFERENCES PRODUCTS(product_id)
);
