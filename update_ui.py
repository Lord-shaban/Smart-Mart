import os

cashier_html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Smart Mart - POS / Cashier</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        body { background-color: #f4f6f9; }
        .navbar { background-color: #2c3e50; }
        .card { border: none; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); margin-bottom: 20px; }
        .total-display { background: #27ae60; color: white; padding: 20px; border-radius: 10px; font-size: 2rem; font-weight: bold; text-align: center; }
        .btn-checkout { font-size: 1.2rem; font-weight: bold; width: 100%; padding: 15px; }
        .print-only { display: none; }
        @media print {
            body * { visibility: hidden; }
            #receipt, #receipt * { visibility: visible; }
            #receipt { position: absolute; left: 0; top: 0; width: 100%; font-family: monospace; }
        }
    </style>
</head>
<body>
    <nav class="navbar navbar-dark mb-4 shadow-sm">
        <div class="container-fluid">
            <span class="navbar-brand mb-0 h1"><i class="fas fa-store me-2"></i>Smart Mart POS</span>
            <span class="text-white"><i class="fas fa-user-circle me-1"></i> Cashier: Alice</span>
        </div>
    </nav>

    <div class="container-fluid px-4">
        <div class="row">
            <!-- Left Panel -->
            <div class="col-lg-4">
                <div class="card">
                    <div class="card-header bg-white border-bottom-0 pt-4 pb-0">
                        <h5 class="card-title text-primary"><i class="fas fa-barcode me-2"></i>Product Search</h5>
                    </div>
                    <div class="card-body">
                        <div class="input-group mb-3">
                            <input type="text" class="form-control form-control-lg" id="barcodeInput" placeholder="Scan Barcode (e.g. BC0001)" onkeypress="if(event.key === 'Enter') addProduct()">
                            <button class="btn btn-primary" onclick="addProduct()"><i class="fas fa-plus"></i></button>
                        </div>
                    </div>
                </div>

                <div class="card">
                    <div class="card-header bg-white border-bottom-0 pt-4 pb-0">
                        <h5 class="card-title text-info"><i class="fas fa-users me-2"></i>Customer Info (Optional)</h5>
                    </div>
                    <div class="card-body">
                        <div class="input-group mb-3">
                            <input type="text" class="form-control" id="customerPhone" placeholder="Phone (e.g. 555-0201)" onkeypress="if(event.key === 'Enter') findCustomer()">
                            <button class="btn btn-info text-white" onclick="findCustomer()"><i class="fas fa-search"></i> Find</button>
                        </div>
                        <div id="customerAlert" class="alert alert-secondary d-none" role="alert"></div>
                    </div>
                </div>
            </div>

            <!-- Right Panel -->
            <div class="col-lg-8">
                <div class="card h-100">
                    <div class="card-body d-flex flex-column">
                        <div class="table-responsive flex-grow-1" style="max-height: 400px; overflow-y: auto;">
                            <table class="table table-hover align-middle" id="cartTable">
                                <thead class="table-light sticky-top">
                                    <tr>
                                        <th>Product</th>
                                        <th>Price</th>
                                        <th class="text-center">Qty</th>
                                        <th class="text-end">Subtotal</th>
                                        <th class="text-center">Action</th>
                                    </tr>
                                </thead>
                                <tbody></tbody>
                            </table>
                        </div>
                        
                        <div class="row align-items-center mt-4 border-top pt-3">
                            <div class="col-md-4">
                                <label class="form-label text-muted fw-bold">Payment Method</label>
                                <select class="form-select form-select-lg" id="paymentMethod">
                                    <option value="Cash">💵 Cash</option>
                                    <option value="Card">💳 Card</option>
                                    <option value="Digital">📱 Digital</option>
                                </select>
                            </div>
                            <div class="col-md-4">
                                <div class="total-display">
                                    $<span id="totalAmount">0.00</span>
                                </div>
                            </div>
                            <div class="col-md-4">
                                <button class="btn btn-success btn-checkout" onclick="checkout()">
                                    <i class="fas fa-check-circle me-2"></i>Checkout
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Receipt -->
    <div id="receipt" class="print-only p-3">
        <h2 class="text-center">SMART MART</h2>
        <p class="text-center text-muted"><small>123 Smart St, Tech City</small></p>
        <hr>
        <p><strong>Date:</strong> <span id="r_date"></span></p>
        <p><strong>Cashier ID:</strong> 2</p>
        <hr>
        <table class="table table-borderless table-sm w-100" id="r_items"></table>
        <hr>
        <h4 class="text-end">Total: $<span id="r_total"></span></h4>
        <p class="mb-0"><strong>Payment:</strong> <span id="r_payment"></span></p>
        <p class="mt-0 fw-bold" id="r_loyalty"></p>
        <hr>
        <p class="text-center mt-4">Thank you for shopping at Smart Mart!</p>
    </div>

<script>
    let cart = [];
    let currentCustomer = null;

    async function addProduct() {
        const barcode = document.getElementById('barcodeInput').value;
        if (!barcode) return;

        try {
            const response = await fetch(`/api/products/${barcode}`);
            if (!response.ok) throw new Error('Product not found');
            const product = await response.json();
            
            const existing = cart.find(item => item.product_id === product.product_id);
            if (existing) {
                if(existing.quantity < product.stock_quantity) existing.quantity += 1;
                else alert('Not enough stock!');
            } else {
                cart.push({ ...product, quantity: 1 });
            }
            
            document.getElementById('barcodeInput').value = '';
            renderCart();
        } catch (error) {
            alert(error.message);
        }
    }

    async function findCustomer() {
        const phone = document.getElementById('customerPhone').value;
        const alertBox = document.getElementById('customerAlert');
        if (!phone) return;

        try {
            const response = await fetch(`/api/customers/${phone}`);
            if (!response.ok) throw new Error('Customer not found');
            currentCustomer = await response.json();
            
            alertBox.classList.remove('d-none', 'alert-danger');
            alertBox.classList.add('alert-success');
            alertBox.innerHTML = `<strong>${currentCustomer.name}</strong> <span class="badge bg-warning ms-2">${currentCustomer.member_tier}</span><br><small><i class="fas fa-coins text-warning"></i> ${currentCustomer.loyalty_points} pts</small>`;
        } catch (error) {
            currentCustomer = null;
            alertBox.classList.remove('d-none', 'alert-success');
            alertBox.classList.add('alert-danger');
            alertBox.innerHTML = `<i class="fas fa-exclamation-circle"></i> Customer not found.`;
        }
    }

    function removeFromCart(index) {
        cart.splice(index, 1);
        renderCart();
    }

    function renderCart() {
        const tbody = document.querySelector('#cartTable tbody');
        tbody.innerHTML = '';
        let total = 0;

        cart.forEach((item, index) => {
            const subtotal = item.price * item.quantity;
            total += subtotal;
            tbody.innerHTML += `
                <tr>
                    <td class="fw-bold text-secondary">${item.name}<br><small class="text-muted fw-normal">${item.barcode}</small></td>
                    <td>$${item.price.toFixed(2)}</td>
                    <td class="text-center"><span class="badge bg-primary rounded-pill px-3 py-2 fs-6">${item.quantity}</span></td>
                    <td class="text-end fw-bold">$${subtotal.toFixed(2)}</td>
                    <td class="text-center"><button class="btn btn-outline-danger btn-sm" onclick="removeFromCart(${index})"><i class="fas fa-trash-alt"></i></button></td>
                </tr>
            `;
        });

        document.getElementById('totalAmount').innerText = total.toFixed(2);
    }

    async function checkout() {
        if (cart.length === 0) {
            alert("Cart is empty");
            return;
        }

        const payload = {
            employee_id: 2,
            customer_id: currentCustomer ? currentCustomer.customer_id : null,
            payment_method: document.getElementById('paymentMethod').value,
            items: cart.map(item => ({ product_id: item.product_id, quantity: item.quantity }))
        };

        try {
            const response = await fetch('/api/transactions', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            if (!response.ok) throw new Error('Checkout failed');
            const result = await response.json();

            // Prepare Receipt
            document.getElementById('r_date').innerText = new Date().toLocaleString();
            let rItemsHTML = '';
            cart.forEach(item => {
                rItemsHTML += `<tr><td>${item.name}<br><small class="text-muted">x${item.quantity} @ $${item.price.toFixed(2)}</small></td><td class="text-end align-bottom">$${(item.price * item.quantity).toFixed(2)}</td></tr>`;
            });
            document.getElementById('r_items').innerHTML = rItemsHTML;
            document.getElementById('r_total').innerText = result.total_amount.toFixed(2);
            document.getElementById('r_payment').innerText = payload.payment_method;
            if (currentCustomer) {
                document.getElementById('r_loyalty').innerText = `Points Earned: ${result.loyalty_points_earned}`;
            }

            window.print();

            // Reset
            cart = [];
            currentCustomer = null;
            document.getElementById('customerPhone').value = '';
            document.getElementById('customerAlert').classList.add('d-none');
            renderCart();
        } catch (error) {
            alert(error.message);
        }
    }
</script>
</body>
</html>"""

manager_html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Smart Mart - Manager Dashboard</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        body { background-color: #f4f7f6; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
        .navbar { background-color: #1a252f; }
        .stat-card { border: none; border-radius: 12px; transition: transform 0.2s; color: white; }
        .stat-card:hover { transform: translateY(-5px); }
        .card { border: none; border-radius: 12px; box-shadow: 0 4px 10px rgba(0,0,0,0.06); margin-bottom: 24px; }
        .card-header { background-color: transparent; border-bottom: 1px solid #f0f0f0; padding: 1.25rem 1.5rem; font-weight: bold; }
        .table th { color: #6c757d; font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.5px; }
        .icon-box { width: 48px; height: 48px; border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 24px; background: rgba(255,255,255,0.2); }
    </style>
</head>
<body>
    <nav class="navbar navbar-dark shadow-sm px-4 py-3 mb-4">
        <span class="navbar-brand h1 mb-0 fs-3"><i class="fas fa-chart-line text-info me-2"></i>Smart Mart Admin</span>
        <div class="d-flex text-white align-items-center">
            <span class="me-3"><i class="fas fa-bell text-warning"></i></span>
            <span><img src="https://ui-avatars.com/api/?name=Manager&background=0D8ABC&color=fff" class="rounded-circle me-2" width="35">Manager</span>
        </div>
    </nav>

    <div class="container-fluid px-4">
        <!-- Top Stats Row -->
        <div class="row mb-3">
            <div class="col-xl-3 col-md-6 mb-4">
                <div class="stat-card bg-primary h-100 p-4 shadow-sm">
                    <div class="d-flex justify-content-between align-items-center">
                        <div>
                            <p class="text-light mb-1 fs-6 text-uppercase fw-semibold">Today's Sales</p>
                            <h2 class="mb-0 fw-bold">$<span id="todaysSales">0.00</span></h2>
                        </div>
                        <div class="icon-box"><i class="fas fa-dollar-sign"></i></div>
                    </div>
                </div>
            </div>
            <div class="col-xl-3 col-md-6 mb-4">
                <div class="stat-card bg-danger h-100 p-4 shadow-sm">
                    <div class="d-flex justify-content-between align-items-center">
                        <div>
                            <p class="text-light mb-1 fs-6 text-uppercase fw-semibold">Low Stock Alerts</p>
                            <h2 class="mb-0 fw-bold" id="lowStockCount">0</h2>
                        </div>
                        <div class="icon-box"><i class="fas fa-exclamation-triangle"></i></div>
                    </div>
                </div>
            </div>
        </div>

        <div class="row">
            <!-- Left Column -->
            <div class="col-lg-6">
                <!-- Top Products -->
                <div class="card h-100">
                    <div class="card-header text-primary d-flex align-items-center">
                        <i class="fas fa-trophy me-2 fs-5"></i><span>Top 5 Products (All-Time)</span>
                    </div>
                    <div class="card-body p-0">
                        <table class="table table-hover mb-0" id="topProductsTable">
                            <thead class="bg-light"><tr><th class="ps-4">Product Name</th><th class="text-end pe-4">Units Sold</th></tr></thead>
                            <tbody></tbody>
                        </table>
                    </div>
                </div>
            </div>
            
            <!-- Right Column -->
            <div class="col-lg-6">
                <!-- Demand Forecaster -->
                <div class="card h-100">
                    <div class="card-header text-success d-flex align-items-center">
                        <i class="fas fa-chart-bar me-2 fs-5"></i><span>Demand Forecaster (Smart Trend)</span>
                        <span class="badge bg-success ms-auto rounded-pill">AI Driven</span>
                    </div>
                    <div class="card-body p-0">
                        <table class="table table-hover mb-0" id="demandTable">
                            <thead class="bg-light"><tr><th class="ps-4">Product Name</th><th class="text-center">Trend (Prev -> Last 7 days)</th><th class="text-end pe-4">Increase</th></tr></thead>
                            <tbody></tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>

        <div class="row mt-4">
            <!-- Expiry Predictor -->
            <div class="col-lg-12">
                <div class="card mb-4">
                    <div class="card-header text-warning bg-white d-flex align-items-center">
                        <i class="fas fa-calendar-times me-2 fs-5 text-warning"></i><span class="text-dark">Expiry Predictor (Items expiring in 7 days)</span>
                        <span class="badge bg-warning text-dark ms-auto rounded-pill px-3">Auto-Discount Suggested</span>
                    </div>
                    <div class="card-body p-0">
                        <table class="table table-hover table-striped mb-0 align-middle" id="expiryTable">
                            <thead class="bg-light">
                                <tr>
                                    <th class="ps-4">Product</th>
                                    <th>Expiry Date</th>
                                    <th>Current Price</th>
                                    <th>Suggested Price (20% Off)</th>
                                    <th class="pe-4 text-center">Action</th>
                                </tr>
                            </thead>
                            <tbody></tbody>
                        </table>
                    </div>
                </div>
            </div>
            
            <!-- Low Stock Details -->
            <div class="col-lg-12">
                <div class="card mb-4">
                    <div class="card-header text-danger bg-white d-flex align-items-center">
                        <i class="fas fa-boxes me-2 fs-5"></i><span class="text-dark">Low Stock Details</span>
                    </div>
                    <div class="card-body p-0">
                        <table class="table table-hover mb-0 align-middle" id="lowStockTable">
                            <thead class="bg-light"><tr><th class="ps-4">Product Name</th><th class="text-center">Current Stock</th><th class="text-center">Reorder Level</th></tr></thead>
                            <tbody></tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        async function fetchReports() {
            try {
                const response = await fetch('/api/manager/reports');
                const data = await response.json();

                // 1. Overview
                document.getElementById('todaysSales').innerText = data.todays_sales.toFixed(2);
                
                const topProductsHtml = data.top_products.map(p => `<tr><td class="ps-4 fw-semibold">${p.name}</td><td class="text-end pe-4"><span class="badge bg-primary rounded-pill px-3 py-2">${p.sold}</span></td></tr>`).join('');
                document.querySelector('#topProductsTable tbody').innerHTML = topProductsHtml;

                // 2. Low Stock
                document.getElementById('lowStockCount').innerText = data.low_stock.length;
                const lowStockHtml = data.low_stock.map(p => `<tr><td class="ps-4 fw-semibold text-secondary">${p.name}</td><td class="text-center text-danger fw-bold">${p.stock_quantity} <i class="fas fa-arrow-down ms-1"></i></td><td class="text-center text-muted">${p.reorder_level}</td></tr>`).join('');
                document.querySelector('#lowStockTable tbody').innerHTML = lowStockHtml;

                // 3. Expiry Predictor
                const expiryHtml = data.expiring_soon.map(p => `
                    <tr>
                        <td class="ps-4 fw-semibold">${p.name}</td>
                        <td class="text-danger fw-bold"><i class="far fa-clock me-1"></i>${p.expiry_date}</td>
                        <td class="text-muted"><del>$${p.price.toFixed(2)}</del></td>
                        <td class="text-success fw-bold fs-5">$${p.suggested_discount_price.toFixed(2)}</td>
                        <td class="pe-4 text-center"><button class="btn btn-sm btn-outline-warning">Apply Discount</button></td>
                    </tr>
                `).join('');
                document.querySelector('#expiryTable tbody').innerHTML = expiryHtml;

                // 4. Demand Forecaster
                const demandHtml = data.demand_forecast.map(p => {
                    const diff = p.recent_7_days - p.prev_7_days;
                    return `
                        <tr>
                            <td class="ps-4 fw-semibold">${p.name}</td>
                            <td class="text-center"><span class="text-muted">${p.prev_7_days} unit</span> <i class="fas fa-long-arrow-alt-right mx-2 text-secondary"></i> <span class="text-dark fw-bold">${p.recent_7_days} unit</span></td>
                            <td class="text-end pe-4 text-success fw-bold"><i class="fas fa-level-up-alt me-1"></i> +${diff}</td>
                        </tr>
                    `;
                }).join('');
                document.querySelector('#demandTable tbody').innerHTML = demandHtml;

            } catch (error) {
                console.error('Error fetching reports:', error);
            }
        }
        window.onload = fetchReports;
    </script>
</body>
</html>"""

customer_html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Smart Mart - Customer Portal</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        body { background-color: #f8f9fc; }
        .login-wrapper { min-height: 80vh; display: flex; align-items: center; justify-content: center; }
        .login-card { border: none; border-radius: 12px; box-shadow: 0 10px 30px rgba(0,0,0,0.08); width: 100%; max-width: 400px; padding: 2rem; }
        
        .profile-header { background: linear-gradient(135deg, #1a2980 0%, #26d0ce 100%); color: white; padding: 3rem 0; margin-bottom: 2rem; border-radius: 0 0 20px 20px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); }
        .tier-Gold { color: #f1c40f; text-shadow: 0 0 5px rgba(241,196,15,0.4); }
        .tier-Silver { color: #e0e0e0; }
        .tier-Bronze { color: #cd7f32; }
        
        .rec-card { border: none; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); transition: transform 0.2s; }
        .rec-card:hover { transform: translateY(-5px); box-shadow: 0 6px 12px rgba(0,0,0,0.1); }
        
        .history-card { border: none; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }
    </style>
</head>
<body>

    <!-- Login Screen -->
    <div class="container login-wrapper" id="loginPanel">
        <div class="card login-card text-center">
            <div class="mb-4">
                <i class="fas fa-shopping-basket fa-4x text-primary mb-3"></i>
                <h3 class="fw-bold text-dark">Smart Mart Portal</h3>
                <p class="text-muted">Enter your Customer ID to continue</p>
            </div>
            <div class="input-group mb-3 mb-4">
                <span class="input-group-text bg-white"><i class="fas fa-id-card text-muted"></i></span>
                <input type="number" class="form-control form-control-lg bg-light" id="customerId" placeholder="Customer ID (e.g. 1)">
            </div>
            <button class="btn btn-primary btn-lg w-100 fw-bold shadow-sm" onclick="login()">Access My Profile <i class="fas fa-arrow-right ms-2"></i></button>
        </div>
    </div>

    <!-- Portal Screen -->
    <div id="portalPanel" style="display: none;">
        
        <!-- Navbar style logout -->
        <div class="bg-dark text-white p-2 d-flex justify-content-end px-4">
            <button class="btn btn-outline-light btn-sm" onclick="logout()"><i class="fas fa-sign-out-alt me-1"></i>Logout</button>
        </div>

        <!-- Profile Header -->
        <div class="profile-header text-center position-relative">
            <h1 class="display-5 fw-bold mb-2" id="cName">Welcome!</h1>
            <p class="fs-5 mb-0">Member Tier: <span id="cTier" class="fw-bold"><i class="fas fa-crown ms-1 border-0"></i></span></p>
            
            <div class="position-absolute translate-middle-x bg-white text-dark rounded-pill px-4 py-2 shadow-lg" style="bottom: -20px; left: 50%;">
                <h4 class="mb-0 text-success fw-bold"><i class="fas fa-coins text-warning me-2"></i><span id="cPoints">0</span> Points</h4>
            </div>
        </div>

        <div class="container mt-5">
            <div class="row">
                <!-- Left Col: AI Recommendations -->
                <div class="col-lg-4 mb-4">
                    <h4 class="mb-3 text-primary fw-bold"><i class="fas fa-magic text-warning me-2"></i>Just For You
                        <span class="badge bg-primary bg-opacity-10 text-primary rounded-pill px-2 py-1 ms-2 fs-6" style="vertical-align: middle;">AI Pick</span>
                    </h4>
                    <p class="text-muted small">Based on shoppers like you</p>
                    <div id="recommendationsList"></div>
                </div>

                <!-- Right Col: Purchase History -->
                <div class="col-lg-8">
                    <h4 class="mb-3 text-secondary fw-bold"><i class="fas fa-history me-2"></i>Recent Purchases</h4>
                    <div class="card history-card">
                        <div class="card-body p-0">
                            <div class="table-responsive">
                                <table class="table table-hover table-borderless mb-0 align-middle">
                                    <thead class="table-light border-bottom">
                                        <tr>
                                            <th class="ps-4 py-3">Date</th>
                                            <th>Item</th>
                                            <th class="text-center">Qty</th>
                                            <th class="text-end pe-4">Subtotal</th>
                                        </tr>
                                    </thead>
                                    <tbody id="historyTable"></tbody>
                                </table>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        async function login() {
            const cid = document.getElementById('customerId').value;
            if (!cid) return;

            try {
                const res = await fetch(`/api/customer/${cid}/portal`);
                if (!res.ok) throw new Error("Customer not found. Please try another ID like 1, 2, or 25.");
                
                const data = await res.json();
                
                // Populate Header
                document.getElementById('cName').innerText = `${data.customer.name}`;
                document.getElementById('cTier').innerHTML = `${data.customer.member_tier} <i class="fas fa-crown fs-6"></i>`;
                document.getElementById('cTier').className = `fw-bold tier-${data.customer.member_tier}`;
                document.getElementById('cPoints').innerText = data.customer.loyalty_points;

                // Populate History
                const histHtml = data.history.map(h => `
                    <tr>
                        <td class="ps-4 text-muted small"><i class="far fa-clock me-1"></i>${h.date_time}</td>
                        <td class="fw-semibold text-dark">${h.name}</td>
                        <td class="text-center"><span class="badge bg-secondary rounded-pill">${h.quantity}</span></td>
                        <td class="text-end pe-4 fw-bold text-success">$${h.subtotal.toFixed(2)}</td>
                    </tr>
                `).join('');
                document.getElementById('historyTable').innerHTML = histHtml || "<tr><td colspan='4' class='text-center py-4 text-muted'>No purchase history yet.</td></tr>";

                // Populate Recommendations
                if (data.recommendations.length > 0) {
                    const recHtml = data.recommendations.map(r => `
                        <div class="card rec-card mb-3 border-start border-4 border-info">
                            <div class="card-body d-flex justify-content-between align-items-center py-3">
                                <div>
                                    <h6 class="mb-1 fw-bold text-dark">${r.name}</h6>
                                    <small class="text-muted">${r.category}</small>
                                </div>
                                <div class="text-success fw-bold fs-5">
                                    $${r.price.toFixed(2)}
                                </div>
                            </div>
                        </div>
                    `).join('');
                    document.getElementById('recommendationsList').innerHTML = recHtml;
                } else {
                    document.getElementById('recommendationsList').innerHTML = "<div class='alert alert-light text-center'>No recommendations right now. Keep shopping!</div>";
                }

                // Switch views
                document.getElementById('loginPanel').style.display = 'none';
                document.getElementById('portalPanel').style.display = 'block';

            } catch (err) {
                alert(err.message);
            }
        }

        function logout() {
            document.getElementById('customerId').value = '';
            document.getElementById('loginPanel').style.display = 'flex';
            document.getElementById('portalPanel').style.display = 'none';
        }
    </script>
</body>
</html>"""

os.makedirs('templates', exist_ok=True)
with open('templates/cashier.html', 'w', encoding='utf-8') as f: f.write(cashier_html)
with open('templates/manager.html', 'w', encoding='utf-8') as f: f.write(manager_html)
with open('templates/customer.html', 'w', encoding='utf-8') as f: f.write(customer_html)
print("UI Updated")