"""
Smart Mart — Application Entry Point
======================================
Run this file to start the development server.
Usage: python run.py
"""

from backend import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True, port=5000)
