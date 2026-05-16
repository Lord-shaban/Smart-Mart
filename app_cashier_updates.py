from flask import render_template

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
