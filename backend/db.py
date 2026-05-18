"""
Smart Mart — Database Utilities (MySQL)
========================================
Request-scoped connection management, query helpers,
and standard API response formatters.
"""

import mysql.connector
from mysql.connector import Error
from flask import g, jsonify, current_app


# ── Connection Management ─────────────────────────────────────

def get_db():
    """Get a MySQL connection scoped to the current request."""
    if 'db' not in g:
        g.db = mysql.connector.connect(
            host=current_app.config['DB_HOST'],
            port=current_app.config['DB_PORT'],
            user=current_app.config['DB_USER'],
            password=current_app.config['DB_PASSWORD'],
            database=current_app.config['DB_NAME'],
            charset='utf8mb4',
            collation='utf8mb4_unicode_ci',
            autocommit=False
        )
    return g.db


def close_db(exception=None):
    """Automatically close DB connection when the request ends."""
    db = g.pop('db', None)
    if db is not None and db.is_connected():
        db.close()


# ── Query Helpers ─────────────────────────────────────────────

def _convert_row(row):
    """Convert MySQL types (Decimal, date, datetime, timedelta) to JSON-safe types."""
    from decimal import Decimal
    from datetime import date, datetime, timedelta
    converted = {}
    for k, v in row.items():
        if isinstance(v, Decimal):
            converted[k] = float(v)
        elif isinstance(v, datetime):
            converted[k] = v.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(v, date):
            converted[k] = v.strftime('%Y-%m-%d')
        elif isinstance(v, timedelta):
            converted[k] = str(v)
        else:
            converted[k] = v
    return converted


def query_db(query, args=(), one=False):
    """Execute a SELECT and return rows as dicts with JSON-safe types."""
    db = get_db()
    cur = db.cursor(dictionary=True)
    cur.execute(query, args)
    rv = [_convert_row(row) for row in cur.fetchall()]
    cur.close()
    return (rv[0] if rv else None) if one else rv


def modify_db(query, args=()):
    """Execute an INSERT/UPDATE/DELETE and return lastrowid."""
    db = get_db()
    cur = db.cursor()
    cur.execute(query, args)
    db.commit()
    lastid = cur.lastrowid
    cur.close()
    return lastid


# ── Validation Helpers ────────────────────────────────────────

def validate_required(data, fields):
    """Return a list of missing field names."""
    return [f for f in fields if not data.get(f)]


# ── API Response Helpers ──────────────────────────────────────

def api_error(message, status=400):
    """Return a standard JSON error response."""
    return jsonify({'success': False, 'error': message}), status


def api_success(data=None, message='OK', status=200):
    """Return a standard JSON success response."""
    payload = {'success': True, 'message': message}
    if data is not None:
        payload['data'] = data
    return jsonify(payload), status
