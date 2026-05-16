import sqlite3
import random
from datetime import datetime, timedelta

DB_FILE = 'smartmart.db'

def seed_real_data():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()

    # Clear existing data
    cur.executescript('''
        DELETE FROM TRANSACTION_ITEMS;
        DELETE FROM TRANSACTIONS;
        DELETE FROM EXPIRY_ALERTS;
        DELETE FROM PRODUCTS;
        DELETE FROM EMPLOYEES;
        DELETE FROM CUSTOMERS;
        DELETE FROM SUPPLIERS;
    ''')
    
    # 1. Real Suppliers
    suppliers = [
        'Almarai Company', 'Coca-Cola Bottlers', 'Nestle Middle East', 
        'Fresh Farms Local', 'Procter & Gamble', 'Pepsico Arabia', 
        'Unilever', 'Savola Group', 'Tyson Foods', 'Kraft Heinz'
    ]
    for i, s_name in enumerate(suppliers):
        cur.execute("INSERT INTO SUPPLIERS (name, contact_person, phone, email) VALUES (?, ?, ?, ?)",
                    (s_name, f"Rep of {s_name.split()[0]}", f"555-10{i:02d}", f"contact@{s_name.split()[0].lower().replace('&','n')}.com"))

    # 2. Real Customers
    first_names = ['Ahmad', 'Sarah', 'Mohammed', 'Emma', 'Omar', 'Laila', 'Khaled', 'Noura', 'Tariq', 'Maha', 'John', 'Fatima', 'Ali', 'Aisha', 'Hassan', 'Rami', 'Dina']
    last_names = ['Ali', 'Smith', 'Hassan', 'Al-Qahtani', 'Youssef', 'Mahmoud', 'Saad', 'Ibrahim', 'Abdullah', 'Johnson', 'Williams', 'Sayed']
    for i in range(1, 101):
        name = f"{random.choice(first_names)} {random.choice(last_names)}"
        tier = random.choice(['Bronze', 'Silver', 'Gold'])
        cur.execute("INSERT INTO CUSTOMERS (name, phone, email, loyalty_points, member_tier) VALUES (?, ?, ?, ?, ?)",
                    (name, f"555-020{i:02d}", f"customer{i}@mail.com", random.randint(10, 2000), tier))

    # 3. Real Employees
    cur.execute("INSERT INTO EMPLOYEES (name, role, shift, birth_date) VALUES ('Alice (Manager)', 'Manager', 'Day', '1985-04-12')")
    cur.execute("INSERT INTO EMPLOYEES (name, role, shift, birth_date) VALUES ('Bob (Cashier)', 'Cashier', 'Day', '1990-08-25')")
    cur.execute("INSERT INTO EMPLOYEES (name, role, shift, birth_date) VALUES ('Charlie (Cashier)', 'Cashier', 'Night', '1995-11-03')")

    # 4. Real Products
    product_catalog = {
        'Beverages': [('Coca Cola 330ml', 1.00), ('Pepsi 330ml', 1.00), ('Sprite 330ml', 1.00), ('Almarai Orange Juice 1L', 2.50), ('Lipton Iced Tea 320ml', 1.50), ('Nescafe Classic 200g', 6.00), ('Aquafina Water 600ml', 0.50), ('Red Bull Energy Drink 250ml', 2.50)],
        'Snacks': [('Lays Classic Chips 170g', 2.00), ('Doritos Nacho Cheese 150g', 2.20), ('Cheetos Spicy 150g', 2.20), ('Oreo Cookies 120g', 1.50), ('Snickers Chocolate Bar 50g', 1.00), ('KitKat 4-Finger 45g', 1.00), ('Bounty Coconut 50g', 1.00), ('Pringles Original 165g', 3.00)],
        'Dairy': [('Almarai Fresh Milk 1L', 1.80), ('Nada Yoghurt 500g', 1.20), ('Kraft Cheddar Cheese 200g', 3.50), ('Lurpak Butter 100g', 2.50), ('Kiri Cream Cheese 6 Portions', 2.00), ('Activia Probiotic Yoghurt 120g', 0.80)],
        'Produce': [('Fresh Bananas (1kg)', 1.50), ('Red Apples (1kg)', 2.50), ('Green Grapes (1kg)', 4.00), ('Fresh Tomatoes (1kg)', 1.20), ('Potatoes (1kg)', 1.00), ('Red Onions (1kg)', 0.80), ('Fresh Carrots (1kg)', 1.10)],
        'Meat': [('Fresh Beef Steak 500g', 12.00), ('Chicken Breast 450g', 6.50), ('Ground Beef 500g', 8.00), ('Lamb Chops 500g', 15.00), ('Frozen Chicken Nuggets 400g', 5.50)],
        'Bakery': [('White Sliced Bread 600g', 1.20), ('Whole Wheat Bread 600g', 1.50), ('Butter Croissant (1 pc)', 1.00), ('French Baguette', 1.50), ('Chocolate Muffin', 2.00)],
        'Household': [('Fairy Dish Soap 400ml', 2.50), ('Tide Laundry Detergent 2.5kg', 12.00), ('Clorox Bleach 1-Gallon', 4.00), ('Fine Paper Towels 4-Rolls', 3.50), ('Kleenex Tissues 5-Pack', 4.50), ('Dettol Surface Cleaner 500ml', 5.00)]
    }

    barcode_idx = 1
    product_ids = []
    
    for cat, items in product_catalog.items():
        for name, price in items:
            cost = round(price * random.uniform(0.6, 0.8), 2)
            stock = random.randint(15, 100)
            
            # Mix of expiry dates to ensure some trigger the "AI Alerts" (< 7 days)
            days_to_expire = random.choice([3, 5, 8, 15, 30, 90, 180, 365])
            expiry = (datetime.now() + timedelta(days=days_to_expire)).strftime('%Y-%m-%d')
            supplier_id = random.randint(1, 10)
            
            barcode = f"BC{barcode_idx:04d}"
            cur.execute('''INSERT INTO PRODUCTS (barcode, name, category, price, cost_price, stock_quantity, expiry_date, supplier_id) 
                           VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                        (barcode, name, cat, price, cost, stock, expiry, supplier_id))
            product_ids.append(cur.lastrowid)
            barcode_idx += 1

    # 5. Real Transactions
    # Generating ~1200 transactions with some demand bias towards the last 7 days for the "Demand Forecaster" AI
    for i in range(1, 1201):
        customer_id = random.randint(1, 100)
        employee_id = random.randint(2, 3) # Random Cashier
        payment_method = random.choice(['Cash', 'Card', 'Card', 'Digital'])
        
        # Bias the dates to generate meaningful "trends"
        days_ago = random.choices([random.randint(0, 6), random.randint(7, 14), random.randint(15, 30)], weights=[0.5, 0.3, 0.2])[0]
        tx_date = (datetime.now() - timedelta(days=days_ago)).strftime('%Y-%m-%d %H:%M:%S')
        
        cur.execute("INSERT INTO TRANSACTIONS (date_time, customer_id, employee_id, total_amount, payment_method, loyalty_points_earned) VALUES (?, ?, ?, 0, ?, 0)",
                    (tx_date, customer_id, employee_id, payment_method))
        tx_id = cur.lastrowid
        
        total_amount = 0
        # Customers buy 1 to 4 distinct items per transaction
        for _ in range(random.randint(1, 4)):
            product_id = random.choice(product_ids)
            cur.execute("SELECT price FROM PRODUCTS WHERE product_id = ?", (product_id,))
            price = cur.fetchone()[0]
            
            qty = random.randint(1, 3)
            subtotal = price * qty
            total_amount += subtotal
            
            cur.execute("INSERT OR REPLACE INTO TRANSACTION_ITEMS (transaction_id, product_id, quantity, price_at_time, subtotal) VALUES (?, ?, ?, ?, ?)",
                        (tx_id, product_id, qty, price, subtotal))
        
        pts = int(total_amount // 10) # 1 Loyalty point per $10 spent
        cur.execute("UPDATE TRANSACTIONS SET total_amount = ?, loyalty_points_earned = ? WHERE transaction_id = ?",
                    (round(total_amount, 2), pts, tx_id))

    conn.commit()
    conn.close()
    print("Realistic sample data seeded successfully into Smart Mart Database.")

if __name__ == '__main__':
    seed_real_data()