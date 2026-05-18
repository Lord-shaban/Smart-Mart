"""Customers API Blueprint — CRUD + portal with AI recommendations."""

from flask import Blueprint, request, jsonify
import mysql.connector
from backend.db import query_db, modify_db, validate_required, api_error, api_success

bp = Blueprint('customers', __name__)


@bp.route('/api/customers', methods=['GET'])
def get_customers():
    return jsonify(query_db("SELECT * FROM v_customer_lifetime ORDER BY name"))


@bp.route('/api/customers/<phone>', methods=['GET'])
def get_customer_by_phone(phone):
    customer = query_db("SELECT * FROM CUSTOMERS WHERE phone = %s", (phone,), one=True)
    if not customer:
        return api_error('Customer not found', 404)
    return jsonify(customer)


@bp.route('/api/customers', methods=['POST'])
def create_customer():
    data = request.json or {}
    missing = validate_required(data, ['name', 'phone', 'email'])
    if missing:
        return api_error(f"Missing required fields: {', '.join(missing)}")
    try:
        cid = modify_db("INSERT INTO CUSTOMERS (name, phone, email) VALUES (%s,%s,%s)",
                        (data['name'], data['phone'], data['email']))
        return api_success({'customer_id': cid}, 'Customer created', 201)
    except mysql.connector.IntegrityError as e:
        return api_error(f"Duplicate phone or email: {e}")
    except Exception as e:
        return api_error(f"Server error: {e}", 500)


@bp.route('/api/customers/<int:customer_id>', methods=['PUT'])
def update_customer(customer_id):
    data = request.json or {}
    existing = query_db("SELECT * FROM CUSTOMERS WHERE customer_id = %s", (customer_id,), one=True)
    if not existing:
        return api_error('Customer not found', 404)
    try:
        modify_db("UPDATE CUSTOMERS SET name=%s, phone=%s, email=%s WHERE customer_id=%s",
                  (data.get('name', existing['name']), data.get('phone', existing['phone']),
                   data.get('email', existing['email']), customer_id))
        return api_success(message='Customer updated')
    except mysql.connector.IntegrityError as e:
        return api_error(f"Duplicate phone or email: {e}")
    except Exception as e:
        return api_error(f"Update failed: {e}", 500)


@bp.route('/api/customers/<int:customer_id>', methods=['DELETE'])
def delete_customer(customer_id):
    existing = query_db("SELECT * FROM CUSTOMERS WHERE customer_id = %s", (customer_id,), one=True)
    if not existing:
        return api_error('Customer not found', 404)
    modify_db("DELETE FROM CUSTOMERS WHERE customer_id = %s", (customer_id,))
    return api_success(message='Customer deleted')


@bp.route('/api/customer/<int:customer_id>/portal', methods=['GET'])
def customer_portal_data(customer_id):
    """Full portal payload: profile, history, AI recommendations."""
    customer = query_db(
        "SELECT name, loyalty_points, member_tier FROM CUSTOMERS WHERE customer_id = %s",
        (customer_id,), one=True)
    if not customer:
        return api_error('Customer not found', 404)

    history = query_db('''
        SELECT t.date_time, p.name, ti.quantity, ti.subtotal
        FROM TRANSACTIONS t
        JOIN TRANSACTION_ITEMS ti ON t.transaction_id = ti.transaction_id
        JOIN PRODUCTS p ON ti.product_id = p.product_id
        WHERE t.customer_id = %s ORDER BY t.date_time DESC LIMIT 20
    ''', (customer_id,))

    recommendations = query_db('''
        SELECT p.name, p.price, c.name AS category, COUNT(ti.product_id) AS score
        FROM TRANSACTION_ITEMS ti
        JOIN TRANSACTIONS t ON ti.transaction_id = t.transaction_id
        JOIN PRODUCTS p ON ti.product_id = p.product_id
        LEFT JOIN CATEGORIES c ON p.category_id = c.category_id
        WHERE t.customer_id != %s AND t.customer_id IN (
            SELECT DISTINCT t2.customer_id FROM TRANSACTIONS t2
            JOIN TRANSACTION_ITEMS ti2 ON t2.transaction_id = ti2.transaction_id
            WHERE ti2.product_id IN (
                SELECT ti3.product_id FROM TRANSACTION_ITEMS ti3
                JOIN TRANSACTIONS t3 ON ti3.transaction_id = t3.transaction_id
                WHERE t3.customer_id = %s))
          AND p.product_id NOT IN (
            SELECT ti4.product_id FROM TRANSACTION_ITEMS ti4
            JOIN TRANSACTIONS t4 ON ti4.transaction_id = t4.transaction_id
            WHERE t4.customer_id = %s)
          AND p.is_active = 1
        GROUP BY p.product_id ORDER BY score DESC LIMIT 5
    ''', (customer_id, customer_id, customer_id))

    return jsonify({'customer': customer, 'history': history, 'recommendations': recommendations})
