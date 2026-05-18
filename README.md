# Smart Mart — Intelligent Retail Platform

> **Full-Stack ERP System** — POS, Inventory, E-Commerce & AI Analytics

---

## 📁 Project Structure

```
SMART MART/
│
├── run.py                          ← Entry point (python run.py)
├── config.py                       ← App configuration
├── requirements.txt                ← Python dependencies
│
├── 🎨 frontend/                    ← ALL FRONTEND FILES
│   ├── templates/                  ← Jinja2 HTML templates
│   │   ├── base.html               ← Shared layout (DRY)
│   │   ├── index.html              ← Landing page
│   │   ├── cashier.html            ← POS terminal
│   │   ├── manager.html            ← Manager dashboard
│   │   ├── store.html              ← Online store
│   │   └── customer.html           ← Customer portal
│   └── static/                     ← Static assets
│       ├── css/
│       │   └── premium.css         ← Design system
│       └── js/
│           ├── cashier.js          ← POS logic
│           ├── manager.js          ← Dashboard logic
│           ├── store.js            ← Store & cart logic
│           └── customer.js         ← Portal logic
│
├── ⚙️ backend/                     ← ALL BACKEND FILES
│   ├── __init__.py                 ← Application factory
│   ├── db.py                       ← Database utilities
│   ├── routes.py                   ← Page routes
│   └── api/                        ← REST API endpoints
│       ├── __init__.py             ← Blueprint registry
│       ├── products.py             ← Products CRUD
│       ├── customers.py            ← Customers CRUD
│       ├── employees.py            ← Employees CRUD
│       ├── suppliers.py            ← Suppliers CRUD
│       ├── transactions.py         ← POS transactions
│       └── analytics.py            ← Reports & dashboard
│
├── 🗄️ database/                    ← ALL DATABASE FILES
│   ├── schema.sql                  ← 3NF schema (9 tables)
│   └── seed.py                     ← Sample data generator
│
├── 📚 docs/                        ← DOCUMENTATION
│   ├── ACADEMIC_REPORT.md          ← Academic report
│   ├── ER_DIAGRAM.md               ← ER diagram
│   └── VIVA_PREP.md                ← Viva prep notes
│
└── instance/                       ← Runtime data (auto-generated)
    └── smartmart.db                ← SQLite database
```

---

## 🚀 Quick Start

```bash
# 1. Create & activate virtual environment
python -m venv .venv
.venv\Scripts\activate          # Windows
source .venv/bin/activate       # Linux/Mac

# 2. Install dependencies
pip install -r requirements.txt

# 3. Seed the database
python database/seed.py

# 4. Start the server
python run.py
```

Open **http://127.0.0.1:5000**

---

## 📦 Modules

| Module | URL | Description |
|--------|-----|-------------|
| Landing Page | `/` | System overview |
| POS Terminal | `/cashier` | Barcode scanning & checkout |
| Manager Hub | `/manager` | Analytics & AI forecasting |
| Online Store | `/store` | Product browsing & cart |
| Customer Portal | `/customer` | Loyalty & AI recommendations |

---

## 🗄️ Database

- **9 Tables** in 3NF
- **6 Views** for analytics
- **6 Triggers** for business logic
- **24 Indexes** for performance

## 🔧 Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Flask 3.x (Python) |
| Database | MySQL (InnoDB) |
| Frontend | Bootstrap 5 + Vanilla JS |
| Architecture | Factory + Blueprints |

**Database configuration:** Set your DB URI in `config.py`, e.g. `mysql+pymysql://user:pass@host:3306/dbname`.
