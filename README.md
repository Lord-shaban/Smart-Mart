# Smart Mart 🛒

Smart Mart is a comprehensive Point of Sale (POS), Management, and E-commerce integrated system built with Python, Flask, and SQLite. It features advanced SQL-based AI algorithms to offer intelligent recommendations and demand forecasting without the need for complex machine learning models.

## 🌟 Key Features

1. **Cashier POS Interface (`/cashier`)**:
   - Fast barcode scanning (e.g., BC0001).
   - Real-time cart calculation and stock validation.
   - Customer loyalty integration (earn points on purchase).
   - Receipt generation and printing.

2. **Manager Dashboard (`/manager`)**:
   - Real-time gross sales and active inventory tracking.
   - **Low Stock Alerts**.
   - **Expiry Predictions**: Identifies products closest to their expiry dates.
   - **Smart Demand Forecasting**: SQL-based moving average to predict upcoming high-demand items.

3. **Online Store (`/store`)**:
   - Premium Glassmorphism UI with smooth animations.
   - Live category filtering.
   - Floating interactive cart sidebar.
   - Customer ID integration (try IDs 101 to 200).

4. **Customer Portal (`/customer`)**:
   - Loyalty tier status (Gold, Silver, Bronze).
   - Dynamic purchase history.
   - **AI-Powered Recommendations**: "Customers who bought what you bought also bought..." engine powered strictly by relational data algebra (Collaborative Filtering).

## 💻 Tech Stack
- **Backend:** Python 3, Flask
- **Database:** SQLite3
- **Frontend:** HTML5, CSS3, JavaScript (Vanilla), Bootstrap 5, FontAwesome
- **Styling:** Custom Premium CSS Theme (Glassmorphism & Gradients)

## 🚀 How to Run Locally

1. **Clone the repository:**
   ```bash
   git clone <your-repo-link>
   cd "SMART MART"
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv .venv
   ```

3. **Activate the environment:**
   - Windows: `.\.venv\Scripts\activate`
   - Mac/Linux: `source .venv/bin/activate`

4. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

5. **Run the application:**
   ```bash
   python app.py
   ```

6. **Access the Application:**
   - Cashier: `http://localhost:5000/cashier`
   - Manager: `http://localhost:5000/manager`
   - Store: `http://localhost:5000/store`
   - Customer: `http://localhost:5000/customer`

## 🗄️ Database & Demo Data
The system uses SQLite (`smartmart.db`). Real-world sample data has been seeded, including:
- 1200+ simulated transactions
- Customer accounts (IDs start from 101)
- 40+ products across multiple categories with logical expiry dates.
