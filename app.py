from flask import Flask, jsonify, request, render_template
import sqlite3

app = Flask(__name__)
DB_FILE = 'smartmart.db'

def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/api/products', methods=['GET'])
def get_products():
    conn = get_db_connection()
    products = conn.execute('SELECT * FROM PRODUCTS').fetchall()
    conn.close()
    return jsonify([dict(ix) for ix in products])

@app.route('/api/products/<barcode>', methods=['GET'])
def get_product_by_barcode(barcode):
    conn = get_db_connection()
    product = conn.execute('SELECT * FROM PRODUCTS WHERE barcode = ?', (barcode,)).fetchone()
    conn.close()
    if product is None:
        return jsonify({'error': 'Product not found'}), 404
    return jsonify(dict(product))

@app.route('/api/transactions', methods=['POST'])
def create_transaction():
    try:
        data = request.json
        employee_id = data.get('employee_id')
        customer_id = data.get('customer_id')
        items = data.get('items', [])
        payment_method = data.get('payment_method', 'Cash')
        
        if not items:
            return jsonify({'error': 'Transaction must have at least one item'}), 400

        conn = get_db_connection()
        cur = conn.cursor()
        
        # Insert main transaction entry
        cur.execute(
            "INSERT INTO TRANSACTIONS (customer_id, employee_id, total_amount, payment_method) VALUES (?, ?, 0, ?)",
            (customer_id, employee_id, payment_method)
        )
        tx_id = cur.lastrowid
        
        total_amount = 0
        
        for item in items:
            product_id = item['product_id']
            qty = item['quantity']
            
            # Fetch product details
            cur.execute("SELECT price, stock_quantity FROM PRODUCTS WHERE product_id = ?", (product_id,))
            product = cur.fetchone()
            
            if not product or product['stock_quantity'] < qty:
                conn.rollback()
                return jsonify({'error': f"Insufficient stock for product ID {product_id}"}), 400
                
            price = product['price']
            subtotal = price * qty
            total_amount += subtotal
            
            # Update stock
            cur.execute("UPDATE PRODUCTS SET stock_quantity = stock_quantity - ? WHERE product_id = ?", (qty, product_id))
            
            # Insert item
            cur.execute(
                "INSERT INTO TRANSACTION_ITEMS (transaction_id, product_id, quantity, price_at_time, subtotal) VALUES (?, ?, ?, ?, ?)",
                (tx_id, product_id, qty, price, subtotal)
            )
            
        points_earned = int(total_amount // 10)
        
        cur.execute(
            "UPDATE TRANSACTIONS SET total_amount = ?, loyalty_points_earned = ? WHERE transaction_id = ?",
            (total_amount, points_earned, tx_id)
        )
        
        if customer_id:
            cur.execute("UPDATE CUSTOMERS SET loyalty_points = loyalty_points + ? WHERE customer_id = ?", (points_earned, customer_id))
            
        conn.commit()
        conn.close()
        
        return jsonify({
            'message': 'Transaction processed successfully',
            'transaction_id': tx_id,
            'total_amount': total_amount,
            'loyalty_points_earned': points_earned
        }), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/cashier')
def cashier_interface():
    return render_template('cashier.html')

@app.route('/api/customers/<phone>', methods=['GET'])
def get_customer(phone):
    conn = get_db_connection()
    customer = conn.execute('SELECT * FROM CUSTOMERS WHERE phone = ?', (phone,)).fetchone()
    conn.close()
    if customer is None:
        return jsonify({'error': 'Customer not found'}), 404
    return jsonify(dict(customer))

@app.route('/manager')
def manager_dashboard():
    return render_template('manager.html')

@app.route('/api/manager/reports', methods=['GET'])
def manager_reports():
    conn = get_db_connection()
    
    # 1. Today's sales
    todays_sales = conn.execute("SELECT IFNULL(SUM(total_amount), 0) as total FROM TRANSACTIONS WHERE DATE(date_time) = DATE('now')").fetchone()['total']
    
    # 2. Top products all-time
    top_products = conn.execute('''
        SELECT p.name, SUM(ti.quantity) as sold 
        FROM TRANSACTION_ITEMS ti 
        JOIN PRODUCTS p ON ti.product_id = p.product_id 
        GROUP BY p.product_id 
        ORDER BY sold DESC 
        LIMIT 5
    ''').fetchall()

    # 3. Inventory: Low stock alerts
    low_stock = conn.execute("SELECT name, stock_quantity, reorder_level FROM PRODUCTS WHERE stock_quantity <= reorder_level").fetchall()
    
    # 4. Expiry Predictor (Expiring in <= 7 days)
    # Autodiscount logic can be applied implicitly here
    expiring_soon = conn.execute('''
        SELECT name, expiry_date, price, ROUND(price * 0.8, 2) as suggested_discount_price 
        FROM PRODUCTS 
        WHERE expiry_date <= DATE('now', '+7 days') AND expiry_date >= DATE('now')
        LIMIT 10
    ''').fetchall()

    # 5. Demand Forecaster (Compare last 7 days vs previous 7 days)
    demand_forecast = conn.execute('''
        SELECT p.name, 
               SUM(CASE WHEN t.date_time >= DATE('now', '-7 days') THEN ti.quantity ELSE 0 END) as recent_7_days,
               SUM(CASE WHEN t.date_time >= DATE('now', '-14 days') AND t.date_time < DATE('now', '-7 days') THEN ti.quantity ELSE 0 END) as prev_7_days
        FROM TRANSACTION_ITEMS ti
        JOIN TRANSACTIONS t ON ti.transaction_id = t.transaction_id
        JOIN PRODUCTS p ON p.product_id = ti.product_id
        GROUP BY p.product_id
        HAVING recent_7_days > prev_7_days AND prev_7_days > 0
        ORDER BY (recent_7_days - prev_7_days) DESC
        LIMIT 5
    ''').fetchall()

    conn.close()
    
    return jsonify({
        'todays_sales': todays_sales,
        'top_products': [dict(row) for row in top_products],
        'low_stock': [dict(row) for row in low_stock],
        'expiring_soon': [dict(row) for row in expiring_soon],
        'demand_forecast': [dict(row) for row in demand_forecast]
    })

@app.route('/customer')
def customer_portal():
    return render_template('customer.html')

@app.route('/api/customer/<int:customer_id>/portal', methods=['GET'])
def customer_portal_data(customer_id):
    conn = get_db_connection()
    
    # 1. Customer Info
    customer = conn.execute('SELECT name, loyalty_points, member_tier FROM CUSTOMERS WHERE customer_id = ?', (customer_id,)).fetchone()
    if not customer:
         conn.close()
         return jsonify({'error': 'Customer not found'}), 404

    # 2. Purchase History
    history = conn.execute('''
        SELECT t.date_time, p.name, ti.quantity, ti.subtotal
        FROM TRANSACTIONS t
        JOIN TRANSACTION_ITEMS ti ON t.transaction_id = ti.transaction_id
        JOIN PRODUCTS p ON ti.product_id = p.product_id
        WHERE t.customer_id = ?
        ORDER BY t.date_time DESC
        LIMIT 10
    ''', (customer_id,)).fetchall()

    # 3. Smart Recommendations ("Customers who bought what you bought also bought...")
    # Finding products bought by other customers who bought the same products as this customer
    recommendations = conn.execute('''
        SELECT p.name, p.price, p.category, COUNT(ti.product_id) as score
        FROM TRANSACTION_ITEMS ti
        JOIN TRANSACTIONS t ON ti.transaction_id = t.transaction_id
        JOIN PRODUCTS p ON ti.product_id = p.product_id
        WHERE t.customer_id != ? -- Other customers
        AND t.customer_id IN (
            -- Customers who bought what this customer bought
            SELECT DISTINCT t2.customer_id
            FROM TRANSACTIONS t2
            JOIN TRANSACTION_ITEMS ti2 ON t2.transaction_id = ti2.transaction_id
            WHERE ti2.product_id IN (
                -- Products this customer bought
                SELECT product_id FROM TRANSACTION_ITEMS t_inner 
                JOIN TRANSACTIONS t_tx ON t_inner.transaction_id = t_tx.transaction_id
                WHERE t_tx.customer_id = ?
            )
        )
        -- Exclude products the customer already bought
        AND p.product_id NOT IN (
            SELECT product_id FROM TRANSACTION_ITEMS t_inner 
            JOIN TRANSACTIONS t_tx ON t_inner.transaction_id = t_tx.transaction_id
            WHERE t_tx.customer_id = ?
        )
        GROUP BY p.product_id
        ORDER BY score DESC
        LIMIT 5
    ''', (customer_id, customer_id, customer_id)).fetchall()

    conn.close()
    
    return jsonify({
        'customer': dict(customer),
        'history': [dict(row) for row in history],
        'recommendations': [dict(row) for row in recommendations]
    })

@app.route('/store')
def online_store():
    return render_template('store.html')

if __name__ == '__main__':
    app.run(debug=True, port=5000)
