/**
 * Smart Mart — POS Terminal (Cashier Module)
 * ============================================
 * Handles barcode scanning, cart management,
 * customer lookup, and transaction processing.
 */

let cart = [];
let currentCustomer = null;
let employees = [];

// ── Toast helper ─────────────────────────────────────────
function showToast(msg, type = 'success') {
    const icons = {
        success: 'fa-check-circle text-success',
        error: 'fa-times-circle text-danger',
        warning: 'fa-exclamation-triangle text-warning'
    };
    const container = document.getElementById('toastContainer');
    const el = document.createElement('div');
    el.className = `toast-msg ${type}`;
    el.innerHTML = `<i class="fas ${icons[type] || icons.success}"></i> ${msg}`;
    container.appendChild(el);
    setTimeout(() => { el.style.opacity = '0'; setTimeout(() => el.remove(), 300); }, 3000);
}

// ── Live clock ───────────────────────────────────────────
function updateClock() {
    document.getElementById('liveClock').textContent = new Date().toLocaleTimeString();
}
setInterval(updateClock, 1000);
updateClock();

// ── Load employees for selector ──────────────────────────
async function loadEmployees() {
    try {
        const res = await fetch('/api/employees');
        employees = await res.json();
        const sel = document.getElementById('cashierSelect');
        sel.innerHTML = employees
            .filter(e => e.role === 'Cashier')
            .map(e => `<option value="${e.employee_id}">${e.name}</option>`)
            .join('');
    } catch (e) {
        console.error('Failed to load employees:', e);
    }
}

// ── Add product by barcode ───────────────────────────────
async function addProduct() {
    const input = document.getElementById('barcodeInput');
    const barcode = input.value.trim().toUpperCase();
    if (!barcode) return;

    try {
        const res = await fetch(`/api/products/${barcode}`);
        if (!res.ok) throw new Error('Product not found');
        const product = await res.json();

        const existing = cart.find(i => i.product_id === product.product_id);
        if (existing) {
            if (existing.quantity < product.stock_quantity) {
                existing.quantity += 1;
            } else {
                showToast('Maximum stock reached!', 'warning');
                return;
            }
        } else {
            cart.push({ ...product, quantity: 1 });
        }

        input.value = '';
        input.focus();
        renderCart();
        showToast(`Added: ${product.name}`);
    } catch (err) {
        showToast(err.message, 'error');
    }
}

// ── Find customer by phone ───────────────────────────────
async function findCustomer() {
    const phone = document.getElementById('customerPhone').value.trim();
    const box = document.getElementById('customerAlert');
    if (!phone) return;

    try {
        const res = await fetch(`/api/customers/${phone}`);
        if (!res.ok) throw new Error('Not found');
        currentCustomer = await res.json();

        box.classList.remove('d-none', 'alert-danger');
        box.classList.add('alert-success');
        box.innerHTML = `<strong>${currentCustomer.name}</strong>
            <span class="badge bg-warning ms-2">${currentCustomer.member_tier}</span><br>
            <small><i class="fas fa-coins text-warning"></i> ${currentCustomer.loyalty_points} pts</small>`;
        showToast(`Customer linked: ${currentCustomer.name}`);
    } catch (err) {
        currentCustomer = null;
        box.classList.remove('d-none', 'alert-success');
        box.classList.add('alert-danger');
        box.innerHTML = `<i class="fas fa-exclamation-circle"></i> Customer not found.`;
    }
}

// ── Cart operations ──────────────────────────────────────
function changeQty(index, delta) {
    cart[index].quantity += delta;
    if (cart[index].quantity <= 0) cart.splice(index, 1);
    renderCart();
}

function removeFromCart(index) {
    cart.splice(index, 1);
    renderCart();
}

function renderCart() {
    const tbody = document.getElementById('cartBody');
    let total = 0;

    if (cart.length === 0) {
        tbody.innerHTML = `<tr><td colspan="5" class="text-center py-5 text-muted">
            <i class="fas fa-barcode fa-3x mb-3 opacity-25 d-block"></i>Scan a barcode to begin</td></tr>`;
        document.getElementById('totalAmount').textContent = '0.00';
        document.getElementById('cartItemCount').textContent = '0 items';
        return;
    }

    tbody.innerHTML = cart.map((item, i) => {
        const sub = item.price * item.quantity;
        total += sub;
        return `<tr>
            <td class="ps-4"><span class="fw-bold">${item.name}</span><br>
                <small class="text-muted">${item.barcode || ''}</small></td>
            <td>$${item.price.toFixed(2)}</td>
            <td class="text-center">
                <div class="d-inline-flex align-items-center gap-1">
                    <button class="btn btn-sm btn-outline-secondary rounded-circle" style="width:28px;height:28px;padding:0" onclick="changeQty(${i},-1)"><i class="fas fa-minus" style="font-size:10px"></i></button>
                    <span class="fw-bold mx-2">${item.quantity}</span>
                    <button class="btn btn-sm btn-outline-secondary rounded-circle" style="width:28px;height:28px;padding:0" onclick="changeQty(${i},1)"><i class="fas fa-plus" style="font-size:10px"></i></button>
                </div>
            </td>
            <td class="text-end fw-bold">$${sub.toFixed(2)}</td>
            <td class="text-center pe-4">
                <button class="btn btn-sm btn-outline-danger" onclick="removeFromCart(${i})"><i class="fas fa-trash-alt"></i></button>
            </td>
        </tr>`;
    }).join('');

    document.getElementById('totalAmount').textContent = total.toFixed(2);
    document.getElementById('cartItemCount').textContent = `${cart.length} item${cart.length > 1 ? 's' : ''}`;
}

// ── Checkout ─────────────────────────────────────────────
async function checkout() {
    if (cart.length === 0) { showToast('Cart is empty', 'warning'); return; }

    const empId = document.getElementById('cashierSelect').value;
    const payload = {
        employee_id: parseInt(empId) || 2,
        customer_id: currentCustomer ? currentCustomer.customer_id : null,
        payment_method: document.getElementById('paymentMethod').value,
        items: cart.map(i => ({ product_id: i.product_id, quantity: i.quantity }))
    };

    try {
        const res = await fetch('/api/transactions', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        const result = await res.json();
        if (!res.ok) throw new Error(result.error || 'Checkout failed');

        // Populate receipt
        document.getElementById('r_date').textContent = new Date().toLocaleString();
        document.getElementById('r_cashier').textContent = document.getElementById('cashierSelect').selectedOptions[0]?.text || 'Cashier';
        document.getElementById('r_items').innerHTML = cart.map(i =>
            `<tr><td>${i.name}<br><small class="text-muted">x${i.quantity} @ $${i.price.toFixed(2)}</small></td>
             <td class="text-end align-bottom">$${(i.price * i.quantity).toFixed(2)}</td></tr>`
        ).join('');
        document.getElementById('r_total').textContent = result.data.total_amount.toFixed(2);
        document.getElementById('r_payment').textContent = payload.payment_method;
        document.getElementById('r_loyalty').textContent = currentCustomer
            ? `Loyalty Points Earned: ${result.data.loyalty_points_earned}` : '';

        showToast(`Sale completed — $${result.data.total_amount.toFixed(2)}`);

        // Ask to print
        if (confirm('Sale successful! Print receipt?')) window.print();

        // Reset
        cart = [];
        currentCustomer = null;
        document.getElementById('customerPhone').value = '';
        document.getElementById('customerAlert').classList.add('d-none');
        renderCart();
        document.getElementById('barcodeInput').focus();
    } catch (err) {
        showToast(err.message, 'error');
    }
}

// ── Init ─────────────────────────────────────────────────
window.onload = () => { loadEmployees(); renderCart(); };
