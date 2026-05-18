/**
 * Smart Mart — Manager Dashboard Module v2
 * ==========================================
 * Full CRUD for Products & Customers,
 * Analytics overview, and discount management.
 */

let allProducts = [];
let allCustomers = [];
let categoriesList = [];
let suppliersList = [];

// ═══ TAB SWITCHING ═══════════════════════════════════════
function switchTab(tab, btn) {
    document.querySelectorAll('[id^="tab-"]').forEach(t => t.style.display = 'none');
    document.getElementById('tab-' + tab).style.display = 'block';
    document.querySelectorAll('#dashTabs .nav-link-pill').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    if (tab === 'products') loadProductsTable();
    if (tab === 'customers') loadCustomersTable();
}

// ═══ OVERVIEW / REPORTS ══════════════════════════════════
async function fetchReports() {
    try {
        const res = await fetch('/api/manager/reports');
        const d = await res.json();
        document.getElementById('todaysSales').innerText = parseFloat(d.todays_sales).toFixed(2);
        document.getElementById('monthlyRevenue').innerText = parseFloat(d.monthly_revenue).toFixed(2);
        document.getElementById('productCount').innerText = d.product_count;
        document.getElementById('lowStockCount').innerText = d.low_stock.length;

        document.querySelector('#topProductsTable tbody').innerHTML = d.top_products.map(p =>
            `<tr><td class="ps-4 fw-semibold">${p.name}</td><td class="text-end pe-4"><span class="badge bg-primary rounded-pill px-3 py-2">${p.sold}</span></td></tr>`
        ).join('') || '<tr><td colspan="2" class="text-center text-muted py-4">No data</td></tr>';

        document.querySelector('#lowStockTable tbody').innerHTML = d.low_stock.map(p =>
            `<tr><td class="ps-4 fw-semibold">${p.name}</td><td class="text-center text-danger fw-bold">${p.stock_quantity} <i class="fas fa-arrow-down ms-1"></i></td><td class="text-center text-muted">${p.reorder_level}</td></tr>`
        ).join('') || '<tr><td colspan="3" class="text-center text-muted py-4">All stock levels healthy ✓</td></tr>';

        document.querySelector('#expiryTable tbody').innerHTML = d.expiring_soon.map(p =>
            `<tr><td class="ps-4 fw-semibold">${p.name}</td><td><i class="far fa-clock me-1 text-danger"></i>${p.expiry_date}</td><td class="text-muted"><del>$${parseFloat(p.price).toFixed(2)}</del></td><td class="text-success fw-bold">$${parseFloat(p.suggested_discount_price).toFixed(2)}</td><td class="pe-4 text-center"><button class="btn btn-sm btn-outline-warning rounded-pill" onclick="openDiscountModal(${p.product_id},'${p.name}',${p.price})"><i class="fas fa-tag me-1"></i>Discount</button></td></tr>`
        ).join('') || '<tr><td colspan="5" class="text-center text-muted py-4">No products expiring soon ✓</td></tr>';

        document.querySelector('#demandTable tbody').innerHTML = d.demand_forecast.map(p => {
            const diff = p.recent_7_days - p.prev_7_days;
            return `<tr><td class="ps-4 fw-semibold">${p.name}</td><td class="text-center"><span class="text-muted">${p.prev_7_days}</span> <i class="fas fa-arrow-right mx-1 text-muted small"></i> <span class="fw-bold">${p.recent_7_days}</span></td><td class="text-end pe-4 text-success fw-bold"><i class="fas fa-arrow-trend-up me-1"></i>+${diff}</td></tr>`;
        }).join('') || '<tr><td colspan="3" class="text-center text-muted py-4">Not enough data</td></tr>';
    } catch (e) { console.error('Reports error:', e); }
}

// ═══ DISCOUNT ════════════════════════════════════════════
function openDiscountModal(id, name, price) {
    document.getElementById('dm_id').value = id;
    document.getElementById('dm_name').textContent = name;
    document.getElementById('dm_price').textContent = parseFloat(price).toFixed(2);
    document.getElementById('dm_pct').value = 20;
    updateDiscountPreview();
    new bootstrap.Modal(document.getElementById('discountModal')).show();
}

function updateDiscountPreview() {
    const price = parseFloat(document.getElementById('dm_price').textContent);
    const pct = parseInt(document.getElementById('dm_pct').value) || 0;
    document.getElementById('dm_new').textContent = (price * (1 - pct / 100)).toFixed(2);
}

async function confirmDiscount() {
    const id = document.getElementById('dm_id').value;
    const pct = parseInt(document.getElementById('dm_pct').value);
    try {
        const res = await fetch(`/api/manager/apply-discount/${id}`, {
            method: 'POST', headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ discount_pct: pct })
        });
        const data = await res.json();
        if (res.ok) {
            bootstrap.Modal.getInstance(document.getElementById('discountModal')).hide();
            showToast(`Discount applied! New price: $${data.data.new_price}`, 'success');
            fetchReports();
        } else { showToast(data.error, 'error'); }
    } catch (e) { showToast('Error: ' + e.message, 'error'); }
}

// ═══ PRODUCTS CRUD ═══════════════════════════════════════
async function loadProductsTable() {
    try {
        const [pRes, cRes, sRes] = await Promise.all([
            fetch('/api/products'), fetch('/api/categories'), fetch('/api/suppliers')
        ]);
        allProducts = await pRes.json();
        categoriesList = await cRes.json();
        suppliersList = await sRes.json();
        renderProductsTable();
    } catch (e) { console.error(e); }
}

function renderProductsTable() {
    document.querySelector('#productsFullTable tbody').innerHTML = allProducts.map(p => `
        <tr>
            <td class="ps-4"><code class="small">${p.barcode}</code></td>
            <td class="fw-semibold">${p.name}</td>
            <td><span class="badge bg-light text-dark border">${p.category || '—'}</span></td>
            <td class="text-end fw-bold text-success">$${parseFloat(p.price).toFixed(2)}</td>
            <td class="text-center">${p.stock_quantity <= p.reorder_level ? `<span class="text-danger fw-bold">${p.stock_quantity}</span>` : p.stock_quantity}</td>
            <td class="small text-muted">${p.expiry_date || '—'}</td>
            <td class="text-center pe-4">
                <button class="btn btn-ghost btn-sm" onclick="editProduct(${p.product_id})" title="Edit"><i class="fas fa-pen text-primary"></i></button>
                <button class="btn btn-ghost btn-sm" onclick="deleteProduct(${p.product_id},'${p.name.replace(/'/g,"\\'")}')" title="Delete"><i class="fas fa-trash text-danger"></i></button>
            </td>
        </tr>
    `).join('');
}

function openProductModal(product = null) {
    document.getElementById('productModalTitle').textContent = product ? 'Edit Product' : 'Add Product';
    document.getElementById('pm_id').value = product ? product.product_id : '';
    document.getElementById('pm_barcode').value = product ? product.barcode : '';
    document.getElementById('pm_name').value = product ? product.name : '';
    document.getElementById('pm_price').value = product ? product.price : '';
    document.getElementById('pm_cost').value = product ? (product.cost_price || '') : '';
    document.getElementById('pm_stock').value = product ? product.stock_quantity : '0';
    document.getElementById('pm_expiry').value = product ? (product.expiry_date || '') : '';
    document.getElementById('pm_reorder').value = product ? product.reorder_level : '10';
    document.getElementById('pm_error').classList.add('d-none');

    // Populate dropdowns
    const catSel = document.getElementById('pm_category');
    catSel.innerHTML = '<option value="">— None —</option>' + categoriesList.map(c =>
        `<option value="${c.category_id}" ${product && product.category_id == c.category_id ? 'selected' : ''}>${c.name}</option>`
    ).join('');
    const supSel = document.getElementById('pm_supplier');
    supSel.innerHTML = '<option value="">— None —</option>' + suppliersList.map(s =>
        `<option value="${s.supplier_id}" ${product && product.supplier_id == s.supplier_id ? 'selected' : ''}>${s.name}</option>`
    ).join('');

    new bootstrap.Modal(document.getElementById('productModal')).show();
}

async function editProduct(id) {
    if (categoriesList.length === 0) {
        const [cRes, sRes] = await Promise.all([fetch('/api/categories'), fetch('/api/suppliers')]);
        categoriesList = await cRes.json();
        suppliersList = await sRes.json();
    }
    const p = allProducts.find(x => x.product_id === id);
    if (p) openProductModal(p);
}

async function saveProduct() {
    const id = document.getElementById('pm_id').value;
    const payload = {
        barcode: document.getElementById('pm_barcode').value.trim(),
        name: document.getElementById('pm_name').value.trim(),
        category_id: document.getElementById('pm_category').value || null,
        supplier_id: document.getElementById('pm_supplier').value || null,
        price: parseFloat(document.getElementById('pm_price').value),
        cost_price: parseFloat(document.getElementById('pm_cost').value) || null,
        stock_quantity: parseInt(document.getElementById('pm_stock').value) || 0,
        expiry_date: document.getElementById('pm_expiry').value || null,
        reorder_level: parseInt(document.getElementById('pm_reorder').value) || 10
    };
    if (!payload.barcode || !payload.name || !payload.price) {
        document.getElementById('pm_error').textContent = 'Barcode, Name, and Price are required.';
        document.getElementById('pm_error').classList.remove('d-none'); return;
    }
    try {
        const url = id ? `/api/products/${id}` : '/api/products';
        const method = id ? 'PUT' : 'POST';
        const res = await fetch(url, { method, headers: {'Content-Type':'application/json'}, body: JSON.stringify(payload) });
        const data = await res.json();
        if (res.ok) {
            bootstrap.Modal.getInstance(document.getElementById('productModal')).hide();
            showToast(id ? 'Product updated ✓' : 'Product created ✓', 'success');
            loadProductsTable();
        } else {
            document.getElementById('pm_error').textContent = data.error;
            document.getElementById('pm_error').classList.remove('d-none');
        }
    } catch (e) { showToast('Error: ' + e.message, 'error'); }
}

async function deleteProduct(id, name) {
    if (!confirm(`Delete "${name}"? This will deactivate the product.`)) return;
    try {
        const res = await fetch(`/api/products/${id}`, { method: 'DELETE' });
        if (res.ok) { showToast('Product deactivated ✓', 'success'); loadProductsTable(); }
        else { const d = await res.json(); showToast(d.error, 'error'); }
    } catch (e) { showToast('Error: ' + e.message, 'error'); }
}

// ═══ CUSTOMERS CRUD ══════════════════════════════════════
async function loadCustomersTable() {
    try {
        const res = await fetch('/api/customers');
        allCustomers = await res.json();
        renderCustomersTable();
    } catch (e) { console.error(e); }
}

function renderCustomersTable() {
    document.querySelector('#customersFullTable tbody').innerHTML = allCustomers.map(c => `
        <tr>
            <td class="ps-4 text-muted">#${c.customer_id}</td>
            <td class="fw-semibold">${c.name}</td>
            <td class="small">${c.phone || '—'}</td>
            <td class="small text-muted">${c.email || '—'}</td>
            <td class="text-center"><span class="badge bg-success bg-opacity-10 text-success rounded-pill">${c.loyalty_points}</span></td>
            <td class="text-center"><span class="badge ${c.member_tier==='Gold'?'bg-warning bg-opacity-10 text-warning':c.member_tier==='Silver'?'bg-secondary bg-opacity-10 text-secondary':'bg-danger bg-opacity-10 text-danger'} rounded-pill">${c.member_tier}</span></td>
            <td class="text-center pe-4">
                <button class="btn btn-ghost btn-sm" onclick="editCustomer(${c.customer_id})" title="Edit"><i class="fas fa-pen text-primary"></i></button>
                <button class="btn btn-ghost btn-sm" onclick="deleteCustomer(${c.customer_id},'${c.name.replace(/'/g,"\\'")}')" title="Delete"><i class="fas fa-trash text-danger"></i></button>
            </td>
        </tr>
    `).join('');
}

function openCustomerModal(cust = null) {
    document.getElementById('customerModalTitle').textContent = cust ? 'Edit Customer' : 'Add Customer';
    document.getElementById('cm_id').value = cust ? cust.customer_id : '';
    document.getElementById('cm_name').value = cust ? cust.name : '';
    document.getElementById('cm_phone').value = cust ? (cust.phone || '') : '';
    document.getElementById('cm_email').value = cust ? (cust.email || '') : '';
    document.getElementById('cm_error').classList.add('d-none');
    new bootstrap.Modal(document.getElementById('customerModal')).show();
}

function editCustomer(id) {
    const c = allCustomers.find(x => x.customer_id === id);
    if (c) openCustomerModal(c);
}

async function saveCustomer() {
    const id = document.getElementById('cm_id').value;
    const payload = {
        name: document.getElementById('cm_name').value.trim(),
        phone: document.getElementById('cm_phone').value.trim(),
        email: document.getElementById('cm_email').value.trim()
    };
    if (!payload.name || !payload.phone || !payload.email) {
        document.getElementById('cm_error').textContent = 'All fields are required.';
        document.getElementById('cm_error').classList.remove('d-none'); return;
    }
    try {
        const url = id ? `/api/customers/${id}` : '/api/customers';
        const method = id ? 'PUT' : 'POST';
        const res = await fetch(url, { method, headers: {'Content-Type':'application/json'}, body: JSON.stringify(payload) });
        const data = await res.json();
        if (res.ok) {
            bootstrap.Modal.getInstance(document.getElementById('customerModal')).hide();
            showToast(id ? 'Customer updated ✓' : 'Customer created ✓', 'success');
            loadCustomersTable();
        } else {
            document.getElementById('cm_error').textContent = data.error;
            document.getElementById('cm_error').classList.remove('d-none');
        }
    } catch (e) { showToast('Error: ' + e.message, 'error'); }
}

async function deleteCustomer(id, name) {
    if (!confirm(`Delete customer "${name}"? This cannot be undone.`)) return;
    try {
        const res = await fetch(`/api/customers/${id}`, { method: 'DELETE' });
        if (res.ok) { showToast('Customer deleted ✓', 'success'); loadCustomersTable(); }
        else { const d = await res.json(); showToast(d.error, 'error'); }
    } catch (e) { showToast('Error: ' + e.message, 'error'); }
}

// ═══ TOAST ═══════════════════════════════════════════════
function showToast(msg, type = 'success') {
    let box = document.querySelector('.toast-box');
    if (!box) { box = document.createElement('div'); box.className = 'toast-box'; document.body.appendChild(box); }
    const el = document.createElement('div');
    el.className = `toast-msg ${type === 'error' ? 'error' : ''}`;
    el.innerHTML = `<i class="fas ${type==='error'?'fa-circle-xmark text-danger':'fa-circle-check text-success'}"></i> ${msg}`;
    box.appendChild(el);
    setTimeout(() => { el.style.opacity = '0'; setTimeout(() => el.remove(), 300); }, 3500);
}

// ═══ INIT ════════════════════════════════════════════════
window.onload = () => {
    fetchReports();
    // Live update discount preview
    document.getElementById('dm_pct')?.addEventListener('input', updateDiscountPreview);
};
