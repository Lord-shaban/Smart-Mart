"""API Blueprint Registration Module."""

from backend.api import products, customers, employees, suppliers, transactions, analytics

ALL_BLUEPRINTS = [
    products.bp,
    customers.bp,
    employees.bp,
    suppliers.bp,
    transactions.bp,
    analytics.bp,
]
