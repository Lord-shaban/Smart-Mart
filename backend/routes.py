"""
Smart Mart — Page Routes
==========================
Serves the HTML page endpoints (non-API).
Separated from the application factory for clean architecture.
"""

from flask import Blueprint, render_template

pages = Blueprint('pages', __name__)


@pages.route('/')
def index():
    """Landing page — system overview and module links."""
    return render_template('index.html')


@pages.route('/cashier')
def cashier_interface():
    """POS terminal interface for cashiers."""
    return render_template('cashier.html')


@pages.route('/manager')
def manager_dashboard():
    """Manager analytics dashboard."""
    return render_template('manager.html')


@pages.route('/store')
def online_store():
    """Customer-facing online storefront."""
    return render_template('store.html')


@pages.route('/customer')
def customer_portal():
    """Customer loyalty portal with AI recommendations."""
    return render_template('customer.html')
