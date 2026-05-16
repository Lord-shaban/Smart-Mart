import os

store_html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Smart Mart - Premium Store</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        :root { --primary: #2ecc71; --secondary: #2c3e50; }
        body { background-color: #f8f9fa; font-family: 'Inter', sans-serif; overflow-x: hidden; }
        /* Navbar */
        .navbar { background: rgba(255, 255, 255, 0.95); backdrop-filter: blur(10px); box-shadow: 0 2px 15px rgba(0,0,0,0.05); }
        .nav-link { font-weight: 600; color: var(--secondary) !important; }
        
        /* Hero */
        .hero { background: linear-gradient(135deg, rgba(46,204,113,0.1) 0%, rgba(44,62,80,0.1) 100%); padding: 60px 0; border-radius: 20px; margin-top: 20px; text-align: center; }
        .hero h1 { font-weight: 800; color: var(--secondary); letter-spacing: -1px; }
        
        /* Category filters */
        .category-scroll { display: flex; overflow-x: auto; gap: 10px; padding: 10px 0; scrollbar-width: none; }
        .category-scroll::-webkit-scrollbar { display: none; }
        .cat-btn { border-radius: 30px; padding: 8px 20px; font-weight: 600; border: 2px solid transparent; background: white; color: #555; transition: 0.3s; white-space: nowrap; }
        .cat-btn:hover, .cat-btn.active { border-color: var(--primary); color: var(--primary); box-shadow: 0 4px 10px rgba(46,204,113,0.2); }

        /* Products */
        .product-card { border: none; border-radius: 16px; transition: 0.3s; height: 100%; position: relative; overflow: hidden; background: white; }
        .product-card:hover { transform: translateY(-8px); box-shadow: 0 15px 30px rgba(0,0,0,0.08); }
        .img-placeholder { height: 200px; background: #f1f3f5; display: flex; align-items: center; justify-content: center; font-size: 4rem; color: #dee2e6; transition: 0.3s; }
        .product-card:hover .img-placeholder { background: #e9ecef; transform: scale(1.05); }
        .card-body { position: relative; z-index: 2; background: white; padding: 20px; flex-grow: 1; display:flex; flex-direction: column;}
        .price-badge { background: var(--primary); color: white; padding: 5px 12px; border-radius: 8px; font-weight: bold; position: absolute; top: 15px; right: 15px; z-index: 3; box-shadow: 0 4px 10px rgba(46,204,113,0.3);}
        
        /* Cart Sidebar */
        .cart-sidebar { position: fixed; top: 0; right: -450px; width: 400px; max-width: 100%; height: 100vh; background: white; z-index: 1050; box-shadow: -5px 0 30px rgba(0,0,0,0.15); transition: 0.4s cubic-bezier(0.25, 0.8, 0.25, 1); display: flex; flex-direction: column; }
        .cart-sidebar.open { right: 0; }
        .overlay { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.4); z-index: 1040; opacity: 0; visibility: hidden; transition: 0.3s; backdrop-filter: blur(3px); }
        .overlay.show { opacity: 1; visibility: visible; }
        
        .cart-item { display: flex; align-items: center; padding: 15px 0; border-bottom: 1px solid #f1f3f5; }
        .cart-qty-ctrl { display: flex; align-items: center; background: #f8f9fa; border-radius: 8px; overflow: hidden; }
        .cart-qty-ctrl button { border: none; background: none; padding: 5px 10px; color: var(--secondary); transition: 0.2s;}
        .cart-qty-ctrl button:hover { background: #e9ecef; }
        
        /* Modals */
        .modal-content { border-radius: 20px; border: none; }
    </style>
</head>
<body>

    <!-- Navbar -->
    <nav class="navbar navbar-expand-lg sticky-top">
        <div class="container">
            <a class="navbar-brand d-flex align-items-center fw-bold fs-4" href="#">
                <i class="fas fa-leaf text-success me-2 fs-3"></i> Smart Mart
            </a>
            
            <div class="d-flex align-items-center gap-3 ms-auto">
                <div id="authArea">
                    <button class="btn btn-outline-dark fw-bold rounded-pill px-4" data-bs-toggle="modal" data-bs-target="#loginModal">
                        <i class="fas fa-user me-2"></i>Sign In
                    </button>
                </div>
                <button class="btn border-0 position-relative p-2" onclick="toggleCart()">
                    <i class="fas fa-shopping-bag fs-4 text-dark"></i>
                    <span class="position-absolute top-0 start-100 translate-middle badge rounded-pill bg-danger border border-light" id="cartCount" style="padding: 5px 8px;">0</span>
                </button>
            </div>
        </div>
    </nav>

    <!-- Hero -->
    <div class="container">
        <div class="hero">
            <h1>Freshness Delivered Daily</h1>
            <p class="text-muted fs-5 mb-4">Shop the finest quality products with intelligent recommendations.</p>
            <div class="mx-auto" style="max-width: 500px; position: relative;">
                <input type="text" id="searchInput" class="form-control form-control-lg rounded-pill shadow-sm border-0 ps-4 pe-5" placeholder="Search for groceries, snacks..." oninput="renderProducts()">
                <i class="fas fa-search position-absolute top-50 end-0 translate-middle-y me-4 text-muted"></i>
            </div>
        </div>
    </div>

    <!-- Main Content -->
    <div class="container py-4">
        <div class="d-flex justify-content-between align-items-center mb-3">
            <h4 class="fw-bold mb-0">Our Catalog</h4>
        </div>
        
        <!-- Category Filter -->
        <div class="category-scroll mb-4" id="catFilter">
            <button class="cat-btn active" onclick="setCategory('All')">🚀 All Products</button>
            <button class="cat-btn" onclick="setCategory('Beverages')">☕ Beverages</button>
            <button class="cat-btn" onclick="setCategory('Snacks')">🍪 Snacks</button>
            <button class="cat-btn" onclick="setCategory('Dairy')">🧀 Dairy</button>
            <button class="cat-btn" onclick="setCategory('Produce')">🍎 Produce</button>
            <button class="cat-btn" onclick="setCategory('Meat')">🥩 Meat</button>
            <button class="cat-btn" onclick="setCategory('Bakery')">🥐 Bakery</button>
            <button class="cat-btn" onclick="setCategory('Household')">🧼 Household</button>
        </div>

        <!-- Products -->
        <div class="row g-4" id="productGrid"></div>
    </div>

    <!-- Login Modal -->
    <div class="modal fade" id="loginModal" tabindex="-1">
        <div class="modal-dialog modal-dialog-centered">
            <div class="modal-content shadow-lg p-3">
                <div class="modal-header border-0">
                    <h5 class="modal-title fw-bold fs-4">Welcome Back</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    <p class="text-muted">Enter your Customer ID (try 1 to 100) to link your loyalty points.</p>
                    <input type="number" id="loginId" class="form-control form-control-lg bg-light border-0 mb-3" placeholder="Customer ID">
                    <div id="loginError" class="text-danger small mb-3 d-none"><i class="fas fa-exclamation-circle me-1"></i> Invalid ID</div>
                    <button class="btn btn-success btn-lg w-100 fw-bold rounded-pill" onclick="processLogin()">Sign In <i class="fas fa-arrow-right ms-2"></i></button>
                </div>
            </div>
        </div>
    </div>

    <!-- Cart Overlay & Sidebar -->
    <div class="overlay" id="cartOverlay" onclick="toggleCart()"></div>
    <div class="cart-sidebar" id="cartSidebar">
        <div class="p-4 bg-white shadow-sm d-flex justify-content-between align-items-center z-3">
            <h4 class="mb-0 fw-bold"><i class="fas fa-shopping-basket text-success me-2"></i>My Cart</h4>
            <button class="btn-close shadow-none" onclick="toggleCart()"></button>
        </div>
        <div class="flex-grow-1 overflow-auto px-4 py-2" id="cartItems">
            <!-- Items injected here -->
        </div>
        <div class="p-4 bg-light border-top mt-auto">
            <div class="d-flex justify-content-between mb-3 fs-5 fw-bold text-dark">
                <span>Total</span>
                <span class="text-success">$<span id="cartTotal">0.00</span></span>
            </div>
            <button class="btn btn-dark btn-lg w-100 fw-bold rounded-pill shadow" onclick="checkout()">
                Checkout Securely <i class="fas fa-lock ms-2"></i>
            </button>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        let products = [];
        let cart = [];
        let activeCategory = 'All';
        let currentUserId = localStorage.getItem('smartmart_customer_id');

        const catIcons = { 'Beverages': 'fa-coffee', 'Snacks': 'fa-cookie', 'Dairy': 'fa-cheese', 'Produce': 'fa-apple-alt', 'Meat': 'fa-drumstick-bite', 'Bakery': 'fa-bread-slice', 'Household': 'fa-pump-soap' };

        // Initialization
        window.onload = async () => {
            checkAuth();
            await loadProducts();
        };

        function checkAuth() {
            const authArea = document.getElementById('authArea');
            if (currentUserId) {
                authArea.innerHTML = `
                    <div class="dropdown">
                        <button class="btn btn-dark fw-bold rounded-pill px-4 dropdown-toggle" data-bs-toggle="dropdown">
                            <i class="fas fa-user-check me-2"></i>Account
                        </button>
                        <ul class="dropdown-menu dropdown-menu-end border-0 shadow-lg rounded-4 mt-2">
                            <li><a class="dropdown-item py-2 fw-semibold" href="/customer"><i class="fas fa-id-badge text-primary me-2"></i>My Portal</a></li>
                            <li><hr class="dropdown-divider"></li>
                            <li><a class="dropdown-item py-2 text-danger fw-semibold" href="#" onclick="logout()"><i class="fas fa-sign-out-alt me-2"></i>Logout</a></li>
                        </ul>
                    </div>`;
            } else {
                authArea.innerHTML = `
                    <button class="btn btn-outline-dark fw-bold rounded-pill px-4" data-bs-toggle="modal" data-bs-target="#loginModal">
                        <i class="fas fa-user me-2"></i>Sign In
                    </button>`;
            }
        }

        async function processLogin() {
            const id = document.getElementById('loginId').value;
            const err = document.getElementById('loginError');
            if (!id) { err.classList.remove('d-none'); return; }
            
            try {
                const res = await fetch(`/api/customer/${id}/portal`);
                if (!res.ok) throw new Error("Not found");
                
                // Login Success
                localStorage.setItem('smartmart_customer_id', id);
                currentUserId = id;
                document.querySelector('#loginModal .btn-close').click();
                checkAuth();
                err.classList.add('d-none');
            } catch (error) {
                err.classList.remove('d-none');
            }
        }

        function logout() {
            localStorage.removeItem('smartmart_customer_id');
            currentUserId = null;
            cart = [];
            updateCartUI();
            checkAuth();
        }

        async function loadProducts() {
            try {
                const res = await fetch('/api/products');
                products = await res.json();
                renderProducts();
            } catch (err) { console.error(err); }
        }

        function setCategory(cat) {
            activeCategory = cat;
            document.querySelectorAll('.cat-btn').forEach(b => b.classList.remove('active'));
            event.currentTarget.classList.add('active');
            renderProducts();
        }

        function renderProducts() {
            const grid = document.getElementById('productGrid');
            const search = document.getElementById('searchInput').value.toLowerCase();
            grid.innerHTML = '';

            let filtered = products.filter(p => p.name.toLowerCase().includes(search));
            if (activeCategory !== 'All') {
                filtered = filtered.filter(p => p.category === activeCategory);
            }

            filtered.forEach(p => {
                const icon = catIcons[p.category] || 'fa-box';
                grid.innerHTML += `
                    <div class="col-xl-3 col-lg-4 col-md-6 col-sm-6">
                        <div class="product-card">
                            <div class="price-badge">$${p.price.toFixed(2)}</div>
                            <div class="img-placeholder">
                                <i class="fas ${icon} opacity-50"></i>
                            </div>
                            <div class="card-body">
                                <small class="text-primary fw-bold mb-1 d-block">${p.category}</small>
                                <h6 class="card-title fw-bold text-dark mb-3">${p.name}</h6>
                                <div class="mt-auto">
                                    <button class="btn btn-light border w-100 fw-bold hover-success text-dark shadow-sm rounded-pill py-2" onclick="addToCart(${p.product_id})" style="transition:0.2s">
                                        <i class="fas fa-plus me-1"></i> Add
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                `;
            });
        }

        function addToCart(id) {
            const product = products.find(p => p.product_id === id);
            const existing = cart.find(c => c.product_id === id);            
            if (existing) { existing.quantity += 1; }
            else { cart.push({ ...product, quantity: 1 }); }
            updateCartUI();
            
            // Pop open side cart
            document.getElementById('cartSidebar').classList.add('open');
            document.getElementById('cartOverlay').classList.add('show');
        }

        function updateCartQty(index, change) {
            cart[index].quantity += change;
            if (cart[index].quantity <= 0) cart.splice(index, 1);
            updateCartUI();
        }

        function updateCartUI() {
            const cItems = document.getElementById('cartItems');
            let total = 0; let count = 0;
            cItems.innerHTML = '';

            if (cart.length === 0) {
                cItems.innerHTML = `<div class="text-center text-muted mt-5 pt-5"><i class="fas fa-shopping-basket fa-4x mb-3 opacity-25"></i><p class="fs-5">Cart is empty</p></div>`;
            } else {
                cart.forEach((item, index) => {
                    const sub = item.price * item.quantity;
                    total += sub; count += item.quantity;

                    cItems.innerHTML += `
                        <div class="cart-item">
                            <div class="flex-grow-1">
                                <h6 class="fw-bold mb-1">${item.name}</h6>
                                <div class="text-success fw-bold small">$${item.price.toFixed(2)}</div>
                            </div>
                            <div class="d-flex align-items-center gap-3">
                                <div class="cart-qty-ctrl shadow-sm">
                                    <button onclick="updateCartQty(${index}, -1)"><i class="fas fa-minus small"></i></button>
                                    <span class="fw-bold px-2">${item.quantity}</span>
                                    <button onclick="updateCartQty(${index}, 1)"><i class="fas fa-plus small"></i></button>
                                </div>
                            </div>
                        </div>
                    `;
                });
            }
            document.getElementById('cartTotal').innerText = total.toFixed(2);
            document.getElementById('cartCount').innerText = count;
        }

        function toggleCart() {
            document.getElementById('cartSidebar').classList.toggle('open');
            document.getElementById('cartOverlay').classList.toggle('show');
        }

        async function checkout() {
            if(cart.length === 0) return;
            if(!currentUserId) {
                toggleCart();
                new bootstrap.Modal(document.getElementById('loginModal')).show();
                return;
            }

            const payload = {
                employee_id: 2, 
                customer_id: parseInt(currentUserId),
                payment_method: 'Digital',
                items: cart.map(i => ({ product_id: i.product_id, quantity: i.quantity }))
            };

            try {
                const res = await fetch('/api/transactions', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });
                
                if (!res.ok) throw new Error("Checkout failed");
                
                // Show success inside cart
                document.getElementById('cartItems').innerHTML = `
                    <div class="text-center text-success mt-5 pt-5">
                        <i class="fas fa-check-circle fa-4x mb-3"></i>
                        <h4 class="fw-bold">Payment Successful!</h4>
                        <p class="text-muted">Points added to your account.</p>
                        <a href="/customer" class="btn btn-success mt-3 rounded-pill fw-bold px-4">View My Portal</a>
                    </div>`;
                cart = [];
                document.getElementById('cartTotal').innerText = "0.00";
                document.getElementById('cartCount').innerText = "0";
            } catch (err) {
                alert("Checkout error: " + err.message);
            }
        }
    </script>
</body>
</html>"""

customer_html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Smart Mart - My Account</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        body { background-color: #f0f2f5; font-family: 'Inter', sans-serif; }
        
        .top-nav { background: #fff; box-shadow: 0 2px 10px rgba(0,0,0,0.05); padding: 15px 30px; display: flex; justify-content: space-between; align-items: center; }
        .logo-text { color: #2ecc71; font-weight: 800; font-size: 1.5rem; text-decoration: none;}
        
        .auth-container { min-height: 80vh; display: flex; align-items: center; justify-content: center; }
        .auth-card { background: white; border-radius: 24px; padding: 40px; width: 100%; max-width: 450px; box-shadow: 0 10px 40px rgba(0,0,0,0.08); text-align: center; }
        .auth-input { border-radius: 12px; padding: 15px; font-size: 1.1rem; background: #f8f9fa; border: 2px solid transparent; transition: 0.3s;}
        .auth-input:focus { border-color: #2ecc71; background: white; box-shadow: none;}
        .btn-auth { border-radius: 12px; padding: 15px; font-size: 1.1rem; font-weight: bold; background: #2c3e50; color: white; transition: 0.3s;}
        .btn-auth:hover { background: #1a252f; transform: translateY(-2px); }

        .app-layout { display: none; padding: 40px 0; }
        
        .profile-sidebar { background: white; border-radius: 20px; padding: 30px; box-shadow: 0 5px 20px rgba(0,0,0,0.03); text-align: center; position: sticky; top: 20px;}
        .avatar-circle { width: 100px; height: 100px; background: linear-gradient(135deg, #2ecc71, #27ae60); color: white; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 3rem; margin: 0 auto 20px; box-shadow: 0 8px 20px rgba(46,204,113,0.3); }
        .tier-badge { display: inline-flex; align-items: center; gap: 5px; padding: 6px 15px; border-radius: 30px; font-weight: bold; font-size: 0.9rem; margin-top: 10px;}
        .tier-Gold { background: #fff8e1; color: #f39c12; border: 1px solid #ffe082; }
        .tier-Silver { background: #f5f6fa; color: #7f8c8d; border: 1px solid #dcdde1; }
        .tier-Bronze { background: #fbeee6; color: #d35400; border: 1px solid #f5cba7; }

        .dashboard-content { display: flex; flex-direction: column; gap: 30px; }
        .section-card { background: white; border-radius: 20px; padding: 30px; box-shadow: 0 5px 20px rgba(0,0,0,0.03); }
        .section-title { font-weight: 800; color: #2c3e50; margin-bottom: 25px; display: flex; align-items: center; gap: 10px; }
        
        .ai-rec-box { background: #f8f9fa; border-radius: 15px; padding: 20px; border-left: 5px solid #3498db; display: flex; justify-content: space-between; align-items: center; transition: 0.3s;}
        .ai-rec-box:hover { transform: translateX(5px); background: #f1f3f5;}
        
        .history-table th { background: #f8f9fa; color: #7f8c8d; font-weight: 600; text-transform: uppercase; font-size: 0.8rem; letter-spacing: 1px; padding: 15px;}
        .history-table td { padding: 15px; vertical-align: middle; color: #2c3e50; font-weight: 500;}
    </style>
</head>
<body>

    <!-- Top Navigation -->
    <div class="top-nav">
        <a href="/store" class="logo-text"><i class="fas fa-leaf me-2"></i>Smart Mart</a>
        <div id="navActions" class="d-none">
            <a href="/store" class="btn btn-outline-success fw-bold rounded-pill px-4 me-2">Go to Store</a>
            <button class="btn btn-light text-danger fw-bold rounded-pill px-4" onclick="logout()">Logout</button>
        </div>
    </div>

    <!-- Login Container -->
    <div class="container auth-container" id="loginPanel">
        <div class="auth-card">
            <div class="mb-4">
                <div class="avatar-circle mx-auto mb-3" style="width: 80px; height: 80px; font-size: 2.5rem; background: #e9ecef; color: #adb5bd; box-shadow: none;"><i class="fas fa-userLock"></i></div>
                <h3 class="fw-bold text-dark">Customer Portal</h3>
                <p class="text-muted">Enter ID to view personalized AI insights</p>
            </div>
            <input type="number" class="form-control auth-input mb-3" id="customerId" placeholder="Customer ID (e.g. 1)">
            <div id="loginError" class="alert alert-danger d-none p-2 small mb-3 border-0 rounded-3">ID not found. Try numbers 1-100.</div>
            <button class="btn w-100 btn-auth" onclick="login()">Enter Dashboard <i class="fas fa-arrow-right ms-2"></i></button>
        </div>
    </div>

    <!-- Main App Layout -->
    <div class="container app-layout" id="portalPanel">
        <div class="row g-4">
            <!-- Left Sidebar -->
            <div class="col-lg-4 col-md-5">
                <div class="profile-sidebar">
                    <div class="avatar-circle"><i class="fas fa-user-check"></i></div>
                    <h4 class="fw-bold text-dark mb-1" id="cName">Loading...</h4>
                    <div id="cTier" class="tier-badge tier-Gold"><i class="fas fa-star"></i> Gold Member</div>
                    
                    <hr class="my-4" style="border-color: #eee;">
                    
                    <div class="bg-light rounded-4 p-4 mb-3">
                        <p class="text-muted fw-bold mb-1 text-uppercase fs-6">Loyalty Balance</p>
                        <h2 class="text-success fw-bold mb-0 flex align-items-center justify-content-center gap-2">
                            <i class="fas fa-coins text-warning"></i> <span id="cPoints">0</span>
                        </h2>
                    </div>
                </div>
            </div>

            <!-- Right Content -->
            <div class="col-lg-8 col-md-7 dashboard-content">
                
                <!-- Smart AI Recommendations -->
                <div class="section-card">
                    <h4 class="section-title">
                        <i class="fas fa-robot text-primary"></i> 
                        Smart Suggestions
                        <span class="badge bg-primary bg-opacity-10 text-primary border border-primary border-opacity-25 rounded-pill fs-6 ms-auto fw-normal">AI Powered</span>
                    </h4>
                    <p class="text-muted mb-4">Because you bought specific items, you might also like these recommended by our Collaborative Filtering Engine:</p>
                    <div id="recommendationsList" class="d-flex flex-column gap-3">
                        <!-- AI Items -->
                    </div>
                </div>

                <!-- Purchase History -->
                <div class="section-card">
                    <h4 class="section-title"><i class="fas fa-receipt text-secondary"></i> Recent Orders</h4>
                    <div class="table-responsive">
                        <table class="table table-hover history-table mb-0">
                            <thead>
                                <tr>
                                    <th>Date</th>
                                    <th>Product</th>
                                    <th class="text-center">Qty</th>
                                    <th class="text-end">Total</th>
                                </tr>
                            </thead>
                            <tbody id="historyTable">
                                <!-- History Items -->
                            </tbody>
                        </table>
                    </div>
                </div>

            </div>
        </div>
    </div>

    <script>
        // Check Auth on load
        window.onload = () => {
            const savedId = localStorage.getItem('smartmart_customer_id');
            if (savedId) {
                document.getElementById('customerId').value = savedId;
                login();
            }
        };

        async function login() {
            const cid = document.getElementById('customerId').value;
            const errBox = document.getElementById('loginError');
            if (!cid) return;

            try {
                const res = await fetch(`/api/customer/${cid}/portal`);
                if (!res.ok) throw new Error("Invalid ID");
                
                const data = await res.json();
                
                // Sidebar Setup
                document.getElementById('cName').innerText = data.customer.name;
                document.getElementById('cTier').className = `tier-badge tier-${data.customer.member_tier}`;
                document.getElementById('cTier').innerHTML = `<i class="fas fa-star"></i> ${data.customer.member_tier}`;
                document.getElementById('cPoints').innerText = data.customer.loyalty_points.toLocaleString();

                // History
                const histHtml = data.history.map(h => `
                    <tr>
                        <td><span class="text-muted small"><i class="far fa-calendar-alt me-1"></i>${h.date_time.split(' ')[0]}</span></td>
                        <td>${h.name}</td>
                        <td class="text-center"><span class="badge bg-light text-dark border">${h.quantity}</span></td>
                        <td class="text-end text-success fw-bold">$${h.subtotal.toFixed(2)}</td>
                    </tr>
                `).join('');
                document.getElementById('historyTable').innerHTML = histHtml || "<tr><td colspan='4' class='text-center py-4 text-muted'>No orders found. Head to the store!</td></tr>";

                // AI Recommendations
                if (data.recommendations && data.recommendations.length > 0) {
                    const recHtml = data.recommendations.map(r => `
                        <div class="ai-rec-box shadow-sm">
                            <div>
                                <h6 class="fw-bold mb-1 text-dark">${r.name}</h6>
                                <span class="badge bg-secondary rounded-pill fw-normal">${r.category}</span>
                            </div>
                            <div class="text-success fw-bold fs-5">$${r.price.toFixed(2)}</div>
                        </div>
                    `).join('');
                    document.getElementById('recommendationsList').innerHTML = recHtml;
                } else {
                    document.getElementById('recommendationsList').innerHTML = "<div class='alert alert-light text-center border p-4 text-muted'>Buy somewhat to let our AI learn your preferences!</div>";
                }

                // Auth Management
                localStorage.setItem('smartmart_customer_id', cid);
                errBox.classList.add('d-none');
                document.getElementById('loginPanel').style.display = 'none';
                document.getElementById('portalPanel').style.display = 'block';
                document.getElementById('navActions').classList.remove('d-none');

            } catch (err) {
                errBox.classList.remove('d-none');
            }
        }

        function logout() {
            localStorage.removeItem('smartmart_customer_id');
            document.getElementById('customerId').value = '';
            document.getElementById('loginPanel').style.display = 'flex';
            document.getElementById('portalPanel').style.display = 'none';
            document.getElementById('navActions').classList.add('d-none');
        }
    </script>
</body>
</html>"""

with open('templates/store.html', 'w', encoding='utf-8') as f: f.write(store_html)
with open('templates/customer.html', 'w', encoding='utf-8') as f: f.write(customer_html)
print("UI & Integration Successfully Perfected!")