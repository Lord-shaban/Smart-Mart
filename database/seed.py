"""
Smart Mart — Database Seed Script (MySQL)
==========================================
Initialises the MySQL database from schema.sql and populates it
with realistic, production-quality sample data.
"""

import mysql.connector
import random
import os
from datetime import datetime, timedelta

# ── MySQL Connection Settings ─────────────────────────────────
DB_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': 'root',
    'charset': 'utf8mb4',
    'collation': 'utf8mb4_unicode_ci',
}
DB_NAME = 'smartmart'
SCHEMA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'schema.sql')


def get_connection(use_db=True):
    config = dict(DB_CONFIG)
    if use_db:
        config['database'] = DB_NAME
    conn = mysql.connector.connect(**config)
    return conn


def init_db():
    """Drop and recreate the database, then load schema via mysql CLI."""
    import subprocess
    
    conn = get_connection(use_db=False)
    cur = conn.cursor()
    cur.execute(f"DROP DATABASE IF EXISTS {DB_NAME}")
    cur.execute(f"CREATE DATABASE {DB_NAME} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
    conn.commit()
    cur.close()
    conn.close()

    # Load schema via mysql CLI (handles DELIMITER for triggers)
    mysql_bin = r"C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe"
    result = subprocess.run(
        [mysql_bin, '-u', DB_CONFIG['user'], f"-p{DB_CONFIG['password']}",
         DB_NAME, '--default-character-set=utf8mb4'],
        input=open(SCHEMA_FILE, 'r', encoding='utf-8').read(),
        capture_output=True, text=True
    )
    if result.returncode != 0 and 'ERROR' in result.stderr:
        print(f"[ERROR] Schema load failed: {result.stderr}")
        return
    print("[OK] Schema loaded into MySQL.")


def seed_data():
    conn = get_connection()
    cur = conn.cursor()

    # 1. Categories
    categories = [
        ('Beverages',  'fa-coffee',         'Soft drinks, juices, water, coffee, and tea'),
        ('Snacks',     'fa-cookie',         'Chips, biscuits, chocolate bars, and nuts'),
        ('Dairy',      'fa-cheese',         'Milk, yoghurt, cheese, and butter'),
        ('Produce',    'fa-apple-alt',      'Fresh fruits and vegetables'),
        ('Meat',       'fa-drumstick-bite', 'Fresh and frozen meat products'),
        ('Bakery',     'fa-bread-slice',    'Bread, pastries, and baked goods'),
        ('Household',  'fa-pump-soap',      'Cleaning supplies and household essentials'),
    ]
    cur.executemany("INSERT INTO CATEGORIES (name, icon, description) VALUES (%s,%s,%s)", categories)
    conn.commit()

    cur.execute("SELECT category_id, name FROM CATEGORIES")
    cat_map = {r[1]: r[0] for r in cur.fetchall()}

    # 2. Suppliers
    suppliers = [
        ('Almarai Company',    'Khalid Al-Rashid', '555-1001', 'contact@almarai.com',   'Riyadh, SA'),
        ('Coca-Cola Bottlers', 'James Wilson',     '555-1002', 'contact@cocacola.com',   'Atlanta, USA'),
        ('Nestle Middle East', 'Sophie Laurent',   '555-1003', 'contact@nestle.com',     'Dubai, UAE'),
        ('Fresh Farms Local',  'Ahmed Mansour',    '555-1004', 'contact@freshfarms.com', 'Amman, JO'),
        ('Procter & Gamble',   'David Chen',       '555-1005', 'contact@pg.com',         'Cincinnati, USA'),
        ('PepsiCo Arabia',     'Nora Al-Faisal',   '555-1006', 'contact@pepsico.com',    'Jeddah, SA'),
        ('Unilever',           'Maria Santos',     '555-1007', 'contact@unilever.com',   'London, UK'),
        ('Savola Group',       'Faisal Bin Saeed', '555-1008', 'contact@savola.com',     'Jeddah, SA'),
        ('Tyson Foods',        'Robert Taylor',    '555-1009', 'contact@tysonfoods.com',  'Springdale, USA'),
        ('Kraft Heinz',        'Elena Rossi',      '555-1010', 'contact@kraftheinz.com', 'Chicago, USA'),
    ]
    cur.executemany("INSERT INTO SUPPLIERS (name, contact_person, phone, email, address) VALUES (%s,%s,%s,%s,%s)", suppliers)
    conn.commit()

    # 3. Customers
    first_names = ['Ahmad','Sarah','Mohammed','Emma','Omar','Laila','Khaled','Noura','Tariq','Maha',
                   'John','Fatima','Ali','Aisha','Hassan','Rami','Dina','Youssef','Hana','Sami']
    last_names = ['Ali','Smith','Hassan','Al-Qahtani','Youssef','Mahmoud','Saad','Ibrahim','Abdullah','Johnson']
    for i in range(1, 101):
        name = f"{random.choice(first_names)} {random.choice(last_names)}"
        pts = random.randint(10, 2000)
        tier = 'Gold' if pts >= 1000 else ('Silver' if pts >= 500 else 'Bronze')
        join_date = (datetime.now() - timedelta(days=random.randint(30, 730))).strftime('%Y-%m-%d')
        cur.execute(
            "INSERT INTO CUSTOMERS (name, phone, email, loyalty_points, member_tier, join_date) VALUES (%s,%s,%s,%s,%s,%s)",
            (name, f"555-{2000+i}", f"customer{i}@mail.com", pts, tier, join_date)
        )
    conn.commit()

    # 4. Employees
    employees = [
        ('Alice Thompson', 'Manager', 'Day',      '1985-04-12', '555-3001'),
        ('Bob Martinez',   'Cashier', 'Day',      '1990-08-25', '555-3002'),
        ('Charlie Ahmed',  'Cashier', 'Night',    '1995-11-03', '555-3003'),
        ('Diana Park',     'Cashier', 'Rotating', '1992-06-18', '555-3004'),
    ]
    for name, role, shift, bdate, phone in employees:
        cur.execute("INSERT INTO EMPLOYEES (name, role, shift, birth_date, phone) VALUES (%s,%s,%s,%s,%s)",
                    (name, role, shift, bdate, phone))
    conn.commit()

    # 5. Products
    catalog = {
        'Beverages': [
            ('Coca Cola 330ml', 1.00), ('Pepsi 330ml', 1.00), ('Sprite 330ml', 1.00),
            ('Almarai Orange Juice 1L', 2.50), ('Lipton Iced Tea 320ml', 1.50),
            ('Nescafe Classic 200g', 6.00), ('Aquafina Water 600ml', 0.50), ('Red Bull Energy 250ml', 2.50),
        ],
        'Snacks': [
            ('Lays Classic Chips 170g', 2.00), ('Doritos Nacho 150g', 2.20),
            ('Cheetos Spicy 150g', 2.20), ('Oreo Cookies 120g', 1.50),
            ('Snickers Bar 50g', 1.00), ('KitKat 4-Finger 45g', 1.00),
            ('Bounty Coconut 50g', 1.00), ('Pringles Original 165g', 3.00),
        ],
        'Dairy': [
            ('Almarai Fresh Milk 1L', 1.80), ('Nada Yoghurt 500g', 1.20),
            ('Kraft Cheddar 200g', 3.50), ('Lurpak Butter 100g', 2.50),
            ('Kiri Cream Cheese 6pc', 2.00), ('Activia Probiotic 120g', 0.80),
        ],
        'Produce': [
            ('Fresh Bananas 1kg', 1.50), ('Red Apples 1kg', 2.50),
            ('Green Grapes 1kg', 4.00), ('Fresh Tomatoes 1kg', 1.20),
            ('Potatoes 1kg', 1.00), ('Red Onions 1kg', 0.80), ('Fresh Carrots 1kg', 1.10),
        ],
        'Meat': [
            ('Beef Steak 500g', 12.00), ('Chicken Breast 450g', 6.50),
            ('Ground Beef 500g', 8.00), ('Lamb Chops 500g', 15.00), ('Chicken Nuggets 400g', 5.50),
        ],
        'Bakery': [
            ('White Bread 600g', 1.20), ('Whole Wheat Bread 600g', 1.50),
            ('Butter Croissant', 1.00), ('French Baguette', 1.50), ('Chocolate Muffin', 2.00),
        ],
        'Household': [
            ('Fairy Dish Soap 400ml', 2.50), ('Tide Detergent 2.5kg', 12.00),
            ('Clorox Bleach 1-Gal', 4.00), ('Fine Paper Towels 4pk', 3.50),
            ('Kleenex Tissues 5pk', 4.50), ('Dettol Cleaner 500ml', 5.00),
        ],
    }

    barcode_idx = 1
    product_ids = []
    for cat_name, items in catalog.items():
        cat_id = cat_map[cat_name]
        for prod_name, price in items:
            cost = round(price * random.uniform(0.55, 0.75), 2)
            stock = random.randint(15, 120)
            days_exp = random.choice([3, 5, 7, 15, 30, 60, 90, 180, 365])
            expiry = (datetime.now() + timedelta(days=days_exp)).strftime('%Y-%m-%d')
            cur.execute(
                "INSERT INTO PRODUCTS (barcode, name, category_id, price, cost_price, "
                "stock_quantity, expiry_date, supplier_id, reorder_level) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                (f"BC{barcode_idx:04d}", prod_name, cat_id, price, cost, stock, expiry,
                 random.randint(1, 10), 10)
            )
            product_ids.append(cur.lastrowid)
            barcode_idx += 1
    conn.commit()

    # 6. Transactions (1200 with demand bias)
    cashier_ids = [2, 3, 4]
    for _ in range(1200):
        cust_id = random.randint(1, 100)
        emp_id = random.choice(cashier_ids)
        payment = random.choice(['Cash', 'Card', 'Card', 'Digital'])
        days_ago = random.choices(
            [random.randint(0, 6), random.randint(7, 14), random.randint(15, 30)],
            weights=[0.50, 0.30, 0.20]
        )[0]
        tx_dt = (datetime.now() - timedelta(days=days_ago, hours=random.randint(8, 21),
                 minutes=random.randint(0, 59))).strftime('%Y-%m-%d %H:%M:%S')

        cur.execute("INSERT INTO TRANSACTIONS (date_time, customer_id, employee_id, total_amount, payment_method) VALUES (%s,%s,%s,0,%s)",
                    (tx_dt, cust_id, emp_id, payment))
        tx_id = cur.lastrowid
        total = 0.0
        used = set()
        for _ in range(random.randint(1, 4)):
            pid = random.choice(product_ids)
            if pid in used:
                continue
            used.add(pid)
            cur.execute("SELECT price FROM PRODUCTS WHERE product_id=%s", (pid,))
            price = cur.fetchone()[0]
            qty = random.randint(1, 3)
            sub = round(float(price) * qty, 2)
            total += sub
            cur.execute("INSERT INTO TRANSACTION_ITEMS (transaction_id, product_id, quantity, price_at_time, subtotal) VALUES (%s,%s,%s,%s,%s)",
                        (tx_id, pid, qty, price, sub))
        pts = int(total // 10)
        cur.execute("UPDATE TRANSACTIONS SET total_amount=%s, loyalty_points_earned=%s WHERE transaction_id=%s",
                    (round(total, 2), pts, tx_id))

    conn.commit()
    conn.close()
    print(f"[OK] Seeded — {len(product_ids)} products, 1200 transactions.")


if __name__ == '__main__':
    init_db()
    seed_data()
