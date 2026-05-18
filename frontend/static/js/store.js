/**
 * Smart Mart — Online Store Module
 * ===================================
 * Handles product browsing, filtering, cart management,
 * authentication, and customer checkout for the storefront.
 */

let products = [];
let cart = [];
let activeCategory = 'All';
let currentUserId = localStorage.getItem('smartmart_customer_id');

const catIcons = {
    'Beverages': 'fa-coffee',
    'Snacks': 'fa-cookie',
    'Dairy': 'fa-cheese',
    'Produce': 'fa-apple-alt',
    'Meat': 'fa-drumstick-bite',
    'Bakery': 'fa-bread-slice',
    'Household': 'fa-pump-soap'
};

// ── Initialization ───────────────────────────────────────
window.onload = async () => {
    checkAuth();
    await loadProducts();
};

// ── Auth management ──────────────────────────────────────
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

// ── Product loading and rendering ────────────────────────
async function loadProducts() {
    try {
        const res = await fetch('/api/products');
        products = await res.json();
        renderProducts();
    } catch (err) {
        console.error('Failed to load products:', err);
    }
}

function setCategory(cat) {
    activeCategory = cat;
    document.querySelectorAll('.cat-pill').forEach(b => b.classList.remove('active'));
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

    filtered.forEach((p, idx) => {
        const icon = catIcons[p.category] || 'fa-box';
        grid.innerHTML += `
            <div class="col-xl-3 col-lg-4 col-md-6 col-sm-6">
                <div class="prod-card anim-up" style="animation-delay:${idx*0.03}s">
                    <div class="prod-price">$${parseFloat(p.price).toFixed(2)}</div>
                    <div class="prod-img">
                        <i class="fas ${icon}" style="opacity:.35"></i>
                    </div>
                    <div class="prod-body">
                        <span class="prod-cat">${p.category}</span>
                        <h6 class="prod-name">${p.name}</h6>
                        <div class="mt-auto pt-2">
                            <button class="btn btn-outline-dark btn-sm w-100 rounded-pill fw-bold" onclick="addToCart(${p.product_id})">
                                <i class="fas fa-plus me-1"></i> Add to Cart
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;
    });
    document.getElementById('prodCountLabel').textContent = `(${filtered.length} items)`;
}

// ── Cart operations ──────────────────────────────────────
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
    let total = 0;
    let count = 0;
    cItems.innerHTML = '';

    if (cart.length === 0) {
        cItems.innerHTML = `<div class="text-center text-muted mt-5 pt-5"><i class="fas fa-shopping-basket fa-4x mb-3 opacity-25"></i><p class="fs-5">Cart is empty</p></div>`;
    } else {
        cart.forEach((item, index) => {
            const sub = item.price * item.quantity;
            total += sub;
            count += item.quantity;

            cItems.innerHTML += `
                <div class="cart-item">
                    <div class="flex-grow-1">
                        <h6 class="fw-bold mb-1">${item.name}</h6>
                <div class="text-success fw-bold small">$${parseFloat(item.price).toFixed(2)}</div>
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

// ── Checkout ─────────────────────────────────────────────
async function checkout() {
    if (cart.length === 0) return;
    if (!currentUserId) {
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
