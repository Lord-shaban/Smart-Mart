"""Analytics API Blueprint — Manager reports, categories, audit log, dashboard."""

from flask import Blueprint, request, jsonify
import mysql.connector
from backend.db import query_db, modify_db, validate_required, api_error, api_success

bp = Blueprint('analytics', __name__)


@bp.route('/api/categories', methods=['GET'])
def get_categories():
    return jsonify(query_db("SELECT * FROM CATEGORIES ORDER BY name"))


@bp.route('/api/categories', methods=['POST'])
def create_category():
    data = request.json or {}
    missing = validate_required(data, ['name'])
    if missing:
        return api_error(f"Missing required fields: {', '.join(missing)}")
    try:
        cid = modify_db("INSERT INTO CATEGORIES (name, icon, description) VALUES (%s,%s,%s)",
                        (data['name'], data.get('icon', 'fa-box'), data.get('description')))
        return api_success({'category_id': cid}, 'Category created', 201)
    except mysql.connector.IntegrityError:
        return api_error('Category already exists')
    except Exception as e:
        return api_error(f"Server error: {e}", 500)


@bp.route('/api/categories/<int:category_id>', methods=['PUT'])
def update_category(category_id):
    data = request.json or {}
    existing = query_db("SELECT * FROM CATEGORIES WHERE category_id = %s", (category_id,), one=True)
    if not existing:
        return api_error('Category not found', 404)
    try:
        modify_db("UPDATE CATEGORIES SET name=%s, icon=%s, description=%s WHERE category_id=%s",
                  (data.get('name', existing['name']), data.get('icon', existing['icon']),
                   data.get('description', existing['description']), category_id))
        return api_success(message='Category updated')
    except Exception as e:
        return api_error(f"Update failed: {e}", 500)


@bp.route('/api/manager/reports', methods=['GET'])
def manager_reports():
    """Aggregated dashboard data for the manager view."""
    todays = query_db(
        "SELECT IFNULL(SUM(total_amount),0) AS total, COUNT(*) AS count "
        "FROM TRANSACTIONS WHERE DATE(date_time) = CURDATE()", one=True)
    monthly = query_db(
        "SELECT IFNULL(SUM(total_amount),0) AS total FROM TRANSACTIONS "
        "WHERE DATE_FORMAT(date_time, '%%Y-%%m') = DATE_FORMAT(NOW(), '%%Y-%%m')", one=True)
    product_count = query_db("SELECT COUNT(*) AS cnt FROM PRODUCTS WHERE is_active = 1", one=True)
    customer_count = query_db("SELECT COUNT(*) AS cnt FROM CUSTOMERS", one=True)

    top_products = query_db('''
        SELECT p.name, c.name AS category, SUM(ti.quantity) AS sold
        FROM TRANSACTION_ITEMS ti JOIN PRODUCTS p ON ti.product_id = p.product_id
        LEFT JOIN CATEGORIES c ON p.category_id = c.category_id
        GROUP BY p.product_id ORDER BY sold DESC LIMIT 5''')

    low_stock = query_db(
        "SELECT name, stock_quantity, reorder_level FROM PRODUCTS "
        "WHERE stock_quantity <= reorder_level AND is_active = 1 ORDER BY stock_quantity ASC")

    expiring_soon = query_db('''
        SELECT p.product_id, p.name, p.expiry_date, p.price,
               ROUND(p.price * 0.8, 2) AS suggested_discount_price
        FROM PRODUCTS p WHERE p.expiry_date <= DATE_ADD(CURDATE(), INTERVAL 7 DAY)
          AND p.expiry_date >= CURDATE() AND p.is_active = 1
        ORDER BY p.expiry_date ASC LIMIT 10''')

    demand_forecast = query_db('''
        SELECT p.name,
            SUM(CASE WHEN t.date_time >= DATE_SUB(CURDATE(), INTERVAL 7 DAY) THEN ti.quantity ELSE 0 END) AS recent_7_days,
            SUM(CASE WHEN t.date_time >= DATE_SUB(CURDATE(), INTERVAL 14 DAY) AND t.date_time < DATE_SUB(CURDATE(), INTERVAL 7 DAY)
                     THEN ti.quantity ELSE 0 END) AS prev_7_days
        FROM TRANSACTION_ITEMS ti
        JOIN TRANSACTIONS t ON ti.transaction_id = t.transaction_id
        JOIN PRODUCTS p ON p.product_id = ti.product_id
        GROUP BY p.product_id
        HAVING recent_7_days > prev_7_days AND prev_7_days > 0
        ORDER BY (recent_7_days - prev_7_days) DESC LIMIT 5''')

    sales_chart = query_db('''
        SELECT DATE(date_time) AS day, ROUND(SUM(total_amount), 2) AS revenue, COUNT(*) AS orders
        FROM TRANSACTIONS WHERE date_time >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)
        GROUP BY DATE(date_time) ORDER BY day ASC''')

    payment_breakdown = query_db('''
        SELECT payment_method, COUNT(*) AS count, ROUND(SUM(total_amount), 2) AS total
        FROM TRANSACTIONS WHERE DATE(date_time) = CURDATE() GROUP BY payment_method''')

    return jsonify({
        'todays_sales': float(todays['total']), 'todays_transactions': todays['count'],
        'monthly_revenue': float(monthly['total']), 'product_count': product_count['cnt'],
        'customer_count': customer_count['cnt'], 'top_products': top_products,
        'low_stock': low_stock, 'expiring_soon': expiring_soon,
        'demand_forecast': demand_forecast, 'sales_chart': sales_chart,
        'payment_breakdown': payment_breakdown,
    })


@bp.route('/api/manager/apply-discount/<int:product_id>', methods=['POST'])
def apply_discount(product_id):
    data = request.json or {}
    discount_pct = float(data.get('discount_pct', 20))
    product = query_db("SELECT * FROM PRODUCTS WHERE product_id = %s", (product_id,), one=True)
    if not product:
        return api_error('Product not found', 404)
    new_price = round(float(product['price']) * (1 - discount_pct / 100), 2)
    modify_db("UPDATE PRODUCTS SET price = %s WHERE product_id = %s", (new_price, product_id))
    modify_db("INSERT INTO EXPIRY_ALERTS (product_id, status, discount_applied) VALUES (%s, 'Resolved', %s)",
              (product_id, discount_pct))
    return api_success({'product_id': product_id, 'old_price': float(product['price']),
                        'new_price': new_price, 'discount_pct': discount_pct}, 'Discount applied')


@bp.route('/api/audit-log', methods=['GET'])
def get_audit_log():
    limit = min(request.args.get('limit', 50, type=int), 200)
    return jsonify(query_db(f"SELECT * FROM AUDIT_LOG ORDER BY performed_at DESC LIMIT {limit}"))


@bp.route('/api/dashboard/stats', methods=['GET'])
def dashboard_stats():
    return jsonify({
        'products': query_db("SELECT COUNT(*) AS c FROM PRODUCTS WHERE is_active=1", one=True)['c'],
        'customers': query_db("SELECT COUNT(*) AS c FROM CUSTOMERS", one=True)['c'],
        'employees': query_db("SELECT COUNT(*) AS c FROM EMPLOYEES WHERE is_active=1", one=True)['c'],
        'suppliers': query_db("SELECT COUNT(*) AS c FROM SUPPLIERS WHERE is_active=1", one=True)['c'],
        'categories': query_db("SELECT COUNT(*) AS c FROM CATEGORIES", one=True)['c'],
        'transactions_today': query_db(
            "SELECT COUNT(*) AS c FROM TRANSACTIONS WHERE DATE(date_time)=CURDATE()", one=True)['c'],
    })
