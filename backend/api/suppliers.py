"""Suppliers API Blueprint — Full CRUD for vendor management."""

from flask import Blueprint, request, jsonify
from backend.db import query_db, modify_db, validate_required, api_error, api_success

bp = Blueprint('suppliers', __name__)


@bp.route('/api/suppliers', methods=['GET'])
def get_suppliers():
    return jsonify(query_db("SELECT * FROM SUPPLIERS WHERE is_active = 1 ORDER BY name"))


@bp.route('/api/suppliers', methods=['POST'])
def create_supplier():
    data = request.json or {}
    missing = validate_required(data, ['name'])
    if missing:
        return api_error(f"Missing required fields: {', '.join(missing)}")
    try:
        sid = modify_db(
            "INSERT INTO SUPPLIERS (name, contact_person, phone, email, address) VALUES (%s,%s,%s,%s,%s)",
            (data['name'], data.get('contact_person'), data.get('phone'),
             data.get('email'), data.get('address')))
        return api_success({'supplier_id': sid}, 'Supplier created', 201)
    except Exception as e:
        return api_error(f"Server error: {e}", 500)


@bp.route('/api/suppliers/<int:supplier_id>', methods=['PUT'])
def update_supplier(supplier_id):
    data = request.json or {}
    existing = query_db("SELECT * FROM SUPPLIERS WHERE supplier_id = %s", (supplier_id,), one=True)
    if not existing:
        return api_error('Supplier not found', 404)
    try:
        modify_db(
            "UPDATE SUPPLIERS SET name=%s, contact_person=%s, phone=%s, email=%s, address=%s WHERE supplier_id=%s",
            (data.get('name', existing['name']), data.get('contact_person', existing['contact_person']),
             data.get('phone', existing['phone']), data.get('email', existing['email']),
             data.get('address', existing['address']), supplier_id))
        return api_success(message='Supplier updated')
    except Exception as e:
        return api_error(f"Update failed: {e}", 500)


@bp.route('/api/suppliers/<int:supplier_id>', methods=['DELETE'])
def delete_supplier(supplier_id):
    existing = query_db("SELECT * FROM SUPPLIERS WHERE supplier_id = %s", (supplier_id,), one=True)
    if not existing:
        return api_error('Supplier not found', 404)
    modify_db("UPDATE SUPPLIERS SET is_active = 0 WHERE supplier_id = %s", (supplier_id,))
    return api_success(message='Supplier deactivated')
