"""Employees API Blueprint — Full CRUD for staff management."""

from flask import Blueprint, request, jsonify
from backend.db import query_db, modify_db, validate_required, api_error, api_success

bp = Blueprint('employees', __name__)


@bp.route('/api/employees', methods=['GET'])
def get_employees():
    return jsonify(query_db("SELECT * FROM EMPLOYEES WHERE is_active = 1 ORDER BY name"))


@bp.route('/api/employees', methods=['POST'])
def create_employee():
    data = request.json or {}
    missing = validate_required(data, ['name', 'role'])
    if missing:
        return api_error(f"Missing required fields: {', '.join(missing)}")
    try:
        eid = modify_db(
            "INSERT INTO EMPLOYEES (name, role, shift, birth_date, phone) VALUES (%s,%s,%s,%s,%s)",
            (data['name'], data['role'], data.get('shift', 'Day'),
             data.get('birth_date'), data.get('phone')))
        return api_success({'employee_id': eid}, 'Employee created', 201)
    except Exception as e:
        return api_error(f"Server error: {e}", 500)


@bp.route('/api/employees/<int:employee_id>', methods=['PUT'])
def update_employee(employee_id):
    data = request.json or {}
    existing = query_db("SELECT * FROM EMPLOYEES WHERE employee_id = %s", (employee_id,), one=True)
    if not existing:
        return api_error('Employee not found', 404)
    try:
        modify_db(
            "UPDATE EMPLOYEES SET name=%s, role=%s, shift=%s, phone=%s WHERE employee_id=%s",
            (data.get('name', existing['name']), data.get('role', existing['role']),
             data.get('shift', existing['shift']), data.get('phone', existing['phone']), employee_id))
        return api_success(message='Employee updated')
    except Exception as e:
        return api_error(f"Update failed: {e}", 500)


@bp.route('/api/employees/<int:employee_id>', methods=['DELETE'])
def delete_employee(employee_id):
    existing = query_db("SELECT * FROM EMPLOYEES WHERE employee_id = %s", (employee_id,), one=True)
    if not existing:
        return api_error('Employee not found', 404)
    modify_db("UPDATE EMPLOYEES SET is_active = 0 WHERE employee_id = %s", (employee_id,))
    return api_success(message='Employee deactivated')
