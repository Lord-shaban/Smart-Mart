"""
Smart Mart — Application Factory (Backend)
=============================================
Creates and configures the Flask application instance.
"""

import os
import mysql.connector
from flask import Flask, request, render_template
from config import Config
from backend.db import close_db, api_error


def create_app(config_class=Config):
    """Create and configure the Flask application."""

    app = Flask(
        __name__,
        template_folder=os.path.join(os.path.dirname(os.path.dirname(__file__)), 'frontend', 'templates'),
        static_folder=os.path.join(os.path.dirname(os.path.dirname(__file__)), 'frontend', 'static')
    )
    app.config.from_object(config_class)

    # ── Register teardown ─────────────────────────────────────
    app.teardown_appcontext(close_db)

    # ── Register Page Routes ──────────────────────────────────
    from backend.routes import pages
    app.register_blueprint(pages)

    # ── Register API Blueprints ───────────────────────────────
    from backend.api import ALL_BLUEPRINTS
    for bp in ALL_BLUEPRINTS:
        app.register_blueprint(bp)

    # ── Error Handlers ────────────────────────────────────────
    @app.errorhandler(404)
    def not_found(e):
        if request.path.startswith('/api/'):
            return api_error('Endpoint not found', 404)
        return render_template('index.html'), 404

    @app.errorhandler(500)
    def server_error(e):
        return api_error('Internal server error', 500)

    return app
