"""Transactions API Blueprint — POS sale processing and history."""

from flask import Blueprint, request, jsonify
from backend.db import get_db, query_db, modify_db, api_error, api_success

bp = Blueprint('transactions', __name__)


@bp.route('/api/transactions', methods=['POST'])
def create_transaction():
    """Process a new sale with stock validation and loyalty points."""
    data = request.json or {}
    employee_id = data.get('employee_id')
    customer_id = data.get('customer_id')
    items = data.get('items', [])
    payment_method = data.get('payment_method', 'Cash')

    if not employee_id:
        return api_error('employee_id is required')
    if not items:
        return api_error('Transaction must have at least one item')

    db = get_db()
    try:
        cur = db.cursor(dictionary=True)
        cur.execute(
            "INSERT INTO TRANSACTIONS (customer_id, employee_id, total_amount, payment_method) VALUES (%s,%s,0,%s)",
            (customer_id, employee_id, payment_method))
        tx_id = cur.lastrowid
        total_amount = 0.0

        for item in items:
            product_id = item.get('product_id')
            qty = int(item.get('quantity', 1))
            if not product_id or qty < 1:
                db.rollback()
                return api_error('Invalid item data')

            cur.execute("SELECT price, stock_quantity FROM PRODUCTS WHERE product_id = %s AND is_active = 1",
                        (product_id,))
            product = cur.fetchone()
            if not product:
                db.rollback()
                return api_error(f"Product ID {product_id} not found")
            if product['stock_quantity'] < qty:
                db.rollback()
                return api_error(f"Insufficient stock for product {product_id} "
                                 f"(available: {product['stock_quantity']}, requested: {qty})")

            price = float(product['price'])
            subtotal = round(price * qty, 2)
            total_amount += subtotal
            cur.execute("UPDATE PRODUCTS SET stock_quantity = stock_quantity - %s WHERE product_id = %s",
                        (qty, product_id))
            cur.execute("INSERT INTO TRANSACTION_ITEMS (transaction_id, product_id, quantity, price_at_time, subtotal) "
                        "VALUES (%s,%s,%s,%s,%s)", (tx_id, product_id, qty, price, subtotal))

        total_amount = round(total_amount, 2)
        points_earned = int(total_amount // 10)
        cur.execute("UPDATE TRANSACTIONS SET total_amount=%s, loyalty_points_earned=%s WHERE transaction_id=%s",
                    (total_amount, points_earned, tx_id))

        if customer_id:
            cur.execute("UPDATE CUSTOMERS SET loyalty_points = loyalty_points + %s WHERE customer_id = %s",
                        (points_earned, customer_id))

        db.commit()
        cur.close()
        return api_success({'transaction_id': tx_id, 'total_amount': total_amount,
                            'loyalty_points_earned': points_earned}, 'Transaction processed', 201)
    except Exception as e:
        db.rollback()
        return api_error(f"Transaction failed: {e}", 500)


@bp.route('/api/transactions/recent', methods=['GET'])
def get_recent_transactions():
    return jsonify(query_db('''
        SELECT t.transaction_id, t.date_time, t.total_amount, t.payment_method,
               t.loyalty_points_earned, c.name AS customer_name, e.name AS employee_name
        FROM TRANSACTIONS t
        LEFT JOIN CUSTOMERS c ON t.customer_id = c.customer_id
        LEFT JOIN EMPLOYEES e ON t.employee_id = e.employee_id
        ORDER BY t.date_time DESC LIMIT 50
    '''))


@bp.route('/api/transactions/<int:transaction_id>', methods=['GET'])
def get_transaction_detail(transaction_id):
    tx = query_db('''
        SELECT t.*, c.name AS customer_name, e.name AS employee_name
        FROM TRANSACTIONS t
        LEFT JOIN CUSTOMERS c ON t.customer_id = c.customer_id
        LEFT JOIN EMPLOYEES e ON t.employee_id = e.employee_id
        WHERE t.transaction_id = %s
    ''', (transaction_id,), one=True)
    if not tx:
        return api_error('Transaction not found', 404)
    items = query_db('''
        SELECT ti.*, p.name AS product_name, p.barcode
        FROM TRANSACTION_ITEMS ti JOIN PRODUCTS p ON ti.product_id = p.product_id
        WHERE ti.transaction_id = %s
    ''', (transaction_id,))
    tx['items'] = items
    return jsonify(tx)
