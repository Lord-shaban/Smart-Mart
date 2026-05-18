"""Products API Blueprint — Full CRUD for product management."""

from flask import Blueprint, request, jsonify
import mysql.connector
from backend.db import query_db, modify_db, validate_required, api_error, api_success

bp = Blueprint('products', __name__)


@bp.route('/api/products', methods=['GET'])
def get_products():
    rows = query_db("SELECT * FROM v_product_details WHERE is_active = 1 ORDER BY name")
    return jsonify(rows)


@bp.route('/api/products/<barcode>', methods=['GET'])
def get_product_by_barcode(barcode):
    product = query_db("SELECT * FROM v_product_details WHERE barcode = %s", (barcode,), one=True)
    if not product:
        return api_error('Product not found', 404)
    return jsonify(product)


@bp.route('/api/products', methods=['POST'])
def create_product():
    data = request.json or {}
    missing = validate_required(data, ['barcode', 'name', 'price'])
    if missing:
        return api_error(f"Missing required fields: {', '.join(missing)}")
    try:
        pid = modify_db(
            "INSERT INTO PRODUCTS (barcode, name, category_id, price, cost_price, "
            "stock_quantity, expiry_date, supplier_id, reorder_level) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)",
            (data['barcode'], data['name'], data.get('category_id'), float(data['price']),
             data.get('cost_price'), int(data.get('stock_quantity', 0)),
             data.get('expiry_date'), data.get('supplier_id'), int(data.get('reorder_level', 10)))
        )
        return api_success({'product_id': pid}, 'Product created', 201)
    except mysql.connector.IntegrityError as e:
        return api_error(f"Integrity error: {e}")
    except Exception as e:
        return api_error(f"Server error: {e}", 500)


@bp.route('/api/products/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    data = request.json or {}
    existing = query_db("SELECT * FROM PRODUCTS WHERE product_id = %s", (product_id,), one=True)
    if not existing:
        return api_error('Product not found', 404)
    try:
        modify_db(
            "UPDATE PRODUCTS SET name=%s, category_id=%s, price=%s, cost_price=%s, "
            "stock_quantity=%s, expiry_date=%s, supplier_id=%s, reorder_level=%s WHERE product_id=%s",
            (data.get('name', existing['name']), data.get('category_id', existing['category_id']),
             float(data.get('price', existing['price'])), data.get('cost_price', existing['cost_price']),
             int(data.get('stock_quantity', existing['stock_quantity'])),
             data.get('expiry_date', existing['expiry_date']),
             data.get('supplier_id', existing['supplier_id']),
             int(data.get('reorder_level', existing['reorder_level'])), product_id)
        )
        return api_success(message='Product updated')
    except Exception as e:
        return api_error(f"Update failed: {e}", 500)


@bp.route('/api/products/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    existing = query_db("SELECT * FROM PRODUCTS WHERE product_id = %s", (product_id,), one=True)
    if not existing:
        return api_error('Product not found', 404)
    modify_db("UPDATE PRODUCTS SET is_active = 0 WHERE product_id = %s", (product_id,))
    return api_success(message='Product deactivated')
