import sqlite3
import random
from datetime import datetime, timedelta

DB_FILE = 'smartmart.db'

def init_db():
    with sqlite3.connect(DB_FILE) as conn:
        with open('schema.sql', 'r') as f:
            conn.executescript(f.read())
            print("Database schema loaded successfully.")

def seed_data():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()

    # Clear existing
    cur.executescript('''
        DELETE FROM TRANSACTION_ITEMS;
        DELETE FROM TRANSACTIONS;
        DELETE FROM EXPIRY_ALERTS;
        DELETE FROM PRODUCTS;
        DELETE FROM EMPLOYEES;
        DELETE FROM CUSTOMERS;
        DELETE FROM SUPPLIERS;
    ''')

    # Seed Suppliers
    for i in range(1, 11):
        cur.execute("INSERT INTO SUPPLIERS (name, contact_person, phone, email) VALUES (?, ?, ?, ?)",
                    (f"Supplier {i}", f"Contact {i}", f"555-010{i}", f"contact{i}@supplier.com"))

    # Seed Customers
    for i in range(1, 101):
        tier = random.choice(['Bronze', 'Silver', 'Gold'])
        cur.execute("INSERT INTO CUSTOMERS (name, phone, email, loyalty_points, member_tier) VALUES (?, ?, ?, ?, ?)",
                    (f"Customer {i}", f"555-020{i}", f"customer{i}@mail.com", random.randint(0, 1000), tier))

    # Seed Employees
    cur.execute("INSERT INTO EMPLOYEES (name, role, shift, birth_date) VALUES ('Alice Manager', 'Manager', 'Day', '1985-04-12')")
    cur.execute("INSERT INTO EMPLOYEES (name, role, shift, birth_date) VALUES ('Bob Cashier', 'Cashier', 'Day', '1990-08-25')")
    cur.execute("INSERT INTO EMPLOYEES (name, role, shift, birth_date) VALUES ('Charlie Cashier', 'Cashier', 'Night', '1995-11-03')")

    # Seed Products
    categories = ['Beverages', 'Snacks', 'Dairy', 'Produce', 'Meat', 'Bakery', 'Household']
    for i in range(1, 501):
        cost = round(random.uniform(1.0, 50.0), 2)
        price = round(cost * random.uniform(1.2, 1.8), 2)
        stock = random.randint(10, 200)
        category = random.choice(categories)
        expiry = (datetime.now() + timedelta(days=random.randint(2, 365))).strftime('%Y-%m-%d')
        supplier_id = random.randint(1, 10)
        
        cur.execute('''INSERT INTO PRODUCTS (barcode, name, category, price, cost_price, stock_quantity, expiry_date, supplier_id) 
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                    (f"BC{i:04d}", f"Product {i}", category, price, cost, stock, expiry, supplier_id))

    # Seed Transactions
    for i in range(1, 1001):
        customer_id = random.randint(1, 100)
        employee_id = random.randint(2, 3) # Cashiers
        payment_method = random.choice(['Cash', 'Card', 'Digital'])
        
        # Transaction in the last 30 days
        tx_date = (datetime.now() - timedelta(days=random.randint(0, 30))).strftime('%Y-%m-%d %H:%M:%S')
        
        cur.execute("INSERT INTO TRANSACTIONS (date_time, customer_id, employee_id, total_amount, payment_method, loyalty_points_earned) VALUES (?, ?, ?, 0, ?, 0)",
                    (tx_date, customer_id, employee_id, payment_method))
        tx_id = cur.lastrowid
        
        # Items in transaction
        total_amount = 0
        for _ in range(random.randint(1, 5)):
            product_id = random.randint(1, 500)
            cur.execute("SELECT price FROM PRODUCTS WHERE product_id = ?", (product_id,))
            price = cur.fetchone()[0]
            
            qty = random.randint(1, 5)
            subtotal = price * qty
            total_amount += subtotal
            
            # Use REPLACE if duplicate product
            cur.execute("INSERT OR REPLACE INTO TRANSACTION_ITEMS (transaction_id, product_id, quantity, price_at_time, subtotal) VALUES (?, ?, ?, ?, ?)",
                        (tx_id, product_id, qty, price, subtotal))
        
        # Update total
        pts = int(total_amount // 10) # 1 point per 10$
        cur.execute("UPDATE TRANSACTIONS SET total_amount = ?, loyalty_points_earned = ? WHERE transaction_id = ?",
                    (total_amount, pts, tx_id))

    conn.commit()
    conn.close()
    print("Database seeded with sample data.")

if __name__ == '__main__':
    init_db()
    seed_data()
