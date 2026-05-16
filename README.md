<div align="center">
  <h1>🛒 Smart Mart ERP & E-commerce System</h1>
  <p>
    <b>A modern, fully-integrated Point of Sale (POS), Inventory Management, and E-commerce platform.</b>
  </p>
  
  [![Python version](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)
  [![Flask](https://img.shields.io/badge/Flask-2.0%2B-black.svg)](https://flask.palletsprojects.com/)
  [![SQLite](https://img.shields.io/badge/Database-SQLite3-green.svg)](https://www.sqlite.org/)
  [![UI](https://img.shields.io/badge/UI-Bootstrap%205-purple.svg)](https://getbootstrap.com/)
  [![License](https://img.shields.io/badge/License-MIT-red.svg)](LICENSE)
</div>

<br/>

## 📖 Overview

**Smart Mart** is an all-in-one business solution built to bridge the gap between physical retail and online shopping. Engineered with Python, Flask, and SQLite, it features native **SQL-based AI algorithms** to deliver smart product recommendations, collaborative filtering, and predictive demand analytics without relying on heavy machine learning frameworks.

Whether you are a Cashier scanning products, a Manager tracking gross margins, or a Customer shopping online, Smart Mart provides a premium, "Glassmorphism" UI experience synchronized across all interfaces in real-time.

---

## ✨ Core Modules & Features

### 1. 💳 Cashier Terminal / POS (/cashier)
- **Fast Barcode Processing:** Instantly scan products (e.g., BC0001).
- **Real-Time Cart Logic:** Calculates subtotals, validates stock, and handles multiple payment gateways (Cash, Card, Digital).
- **Loyalty Program Integration:** Link purchases directly to a Customer ID to award points automatically.
- **Smart Receipts:** Printable, formatted digital receipts for customers.

### 2. 📊 Manager Command Center (/manager)
- **Live Business Analytics:** Monitor daily sales, active inventory, and revenue.
- **Predictive Expiry Alerts:** Alerts for inventory approaching expiration dates.
- **Low Stock Warnings:** Real-time triggers for inventory replenishment.
- **SQL-Based Demand Forecasting:** Utilizing moving averages to predict upcoming high-demand items based on historical transaction volumes.

### 3. 🛍️ Digital Storefront (/store)
- **Premium UI/UX:** Responsive, modern design featuring Glassmorphism, blurred navbars, and animated product cards.
- **Interactive Cart:** Sliding sidebar panel for easy cart modifications.
- **Live Filtering:** Instant category filters (e.g., Beverages, Snacks, Produce).
- **Seamless Auth:** Customers can link their accounts to view points and unified history. *(Use IDs: 101 to 200 to test)*.

### 4. 👤 Customer Hub (/customer)
- **Loyalty Dashboard:** View current tier (Bronze, Silver, Gold) and points balance.
- **Purchase History tracking:** Review past transactions whether bought in-store or online.
- **💡 AI-Powered Recommendations:** "Customers who bought what you bought also bought..." engine, powered by advanced associative SQL queries.

---

## 🛠️ Technology Stack

| Area | Technologies |
| :--- | :--- |
| **Backend Core** | Python 3, Flask, Werkzeug |
| **Database** | SQLite3 (Relational logic & AI triggers) |
| **Frontend UI** | HTML5, Vanilla JavaScript, CSS3 |
| **Styling Frameworks** | Bootstrap 5, FontAwesome 6, Google Fonts |
| **Architecture** | RESTful API, MVC Pattern |

---

## 📂 Project Structure

`	ext
SMART_MART/
├── app.py                  # Main Flask application and API routing
├── schema.sql              # Database schema (Tables, Relations, Views)
├── seed.py                 # Initial sample data generator
├── add_real_data.py        # Generates 1000+ realistic transactions & customers
├── requirements.txt        # Python dependency list
│
├── static/
│   └── css/
│       └── premium.css     # Unified Premium Styling (Glassmorphism & Gradients)
│
└── templates/              # HTML Frontend Views
    ├── cashier.html        # POS Terminal View
    ├── manager.html        # Business Analytics Dashboard
    ├── store.html          # Public E-commerce View
    └── customer.html       # Personalized Customer Hub
`

---

## 🚀 Quick Start Guide

Follow these steps to run the platform locally on your machine.

### Prerequisites
- Python 3.8 or higher
- Git

### Installation Steps

1. **Clone the repository**
   `ash
   git clone https://github.com/Lord-shaban/Smart-Mart.git
   cd Smart-Mart
   `

2. **Create and activate a virtual environment**
   `ash
   # On Windows
   python -m venv .venv
   .\.venv\Scripts\activate
   
   # On macOS/Linux
   python3 -m venv .venv
   source .venv/bin/activate
   `

3. **Install dependencies**
   `ash
   pip install -r requirements.txt
   `

4. **Initialize Database and Demo Data**
   *(Note: The database smartmart.db is already configured, but if you need to reset it, you can rerun the seed scripts).*
   `ash
   python add_real_data.py
   `

5. **Start the Application**
   `ash
   python app.py
   `

6. **Explore the System!** Open your browser and navigate to:
   - 💻 POS: http://localhost:5000/cashier
   - 📈 Manager: http://localhost:5000/manager
   - 🛒 Store: http://localhost:5000/store
   - 👤 Portal: http://localhost:5000/customer

---

## 🧠 The "AI" Concept (without ML packages)

Instead of relying on heavy machine-learning environments (like TensorFlow or PyTorch), this system leverages **Advanced Relational Algebra (SQL)** to mimic intelligence perfectly suited for edge deployments:
- **Collaborative Filtering:** Identifies associated product clusters efficiently by evaluating overlapping cart behaviors.
- **Time-Series Analysis:** Ranks moving transaction volumes to spotlight trending inventory.
This keeps the system blazingly fast, lightweight, and incredibly easy to maintain.

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

<div align="center">
  <b>Built with ❤️ for modern retail integration.</b>
</div>
