/**
 * Smart Mart — Customer Portal Module v2
 * ========================================
 * Auth, profile display, edit profile,
 * purchase history, and AI recommendations.
 */

let currentCustomer = null;

// ── Check Auth on load ───────────────────────────────────
window.onload = () => {
    const savedId = localStorage.getItem('smartmart_customer_id');
    if (savedId) {
        document.getElementById('customerId').value = savedId;
        login();
    }
};

// ── Login ────────────────────────────────────────────────
async function login() {
    const cid = document.getElementById('customerId').value;
    const errBox = document.getElementById('loginError');
    if (!cid) return;

    try {
        const res = await fetch(`/api/customer/${cid}/portal`);
        if (!res.ok) throw new Error("Invalid ID");
        const data = await res.json();
        currentCustomer = { id: cid, ...data.customer };

        // Sidebar
        document.getElementById('cName').innerText = data.customer.name;
        document.getElementById('cTier').className = `tier-pill tier-${data.customer.member_tier}`;
        document.getElementById('cTier').innerHTML = `<i class="fas fa-star"></i> ${data.customer.member_tier}`;
        document.getElementById('cPoints').innerText = data.customer.loyalty_points.toLocaleString();

        // History
        const histHtml = data.history.map(h => `
            <tr>
                <td><span class="text-muted small"><i class="far fa-calendar-alt me-1"></i>${h.date_time.split(' ')[0]}</span></td>
                <td class="fw-semibold">${h.name}</td>
                <td class="text-center"><span class="badge bg-light text-dark border">${h.quantity}</span></td>
                <td class="text-end text-success fw-bold">$${parseFloat(h.subtotal).toFixed(2)}</td>
            </tr>
        `).join('');
        document.getElementById('historyTable').innerHTML = histHtml || "<tr><td colspan='4' class='text-center py-4 text-muted'>No orders yet. <a href='/store' class='text-brand fw-bold'>Start shopping!</a></td></tr>";

        // AI Recommendations
        if (data.recommendations && data.recommendations.length > 0) {
            document.getElementById('recommendationsList').innerHTML = data.recommendations.map(r => `
                <div class="rec-item">
                    <div>
                        <h6 class="fw-bold mb-1" style="font-size:.9rem">${r.name}</h6>
                        <span class="badge bg-secondary bg-opacity-10 text-secondary rounded-pill" style="font-size:.65rem">${r.category}</span>
                    </div>
                    <div class="text-success fw-bold" style="font-size:1.05rem">$${parseFloat(r.price).toFixed(2)}</div>
                </div>
            `).join('');
        } else {
            document.getElementById('recommendationsList').innerHTML = "<div class='text-center text-muted p-4' style='background:var(--bg);border-radius:var(--r)'><i class='fas fa-robot fa-2x mb-2 d-block opacity-25'></i>Make some purchases to activate AI recommendations!</div>";
        }

        // Show portal
        localStorage.setItem('smartmart_customer_id', cid);
        errBox.classList.add('d-none');
        document.getElementById('loginPanel').style.display = 'none';
        document.getElementById('portalPanel').style.display = 'block';
        document.getElementById('navActions').style.display = 'flex';

    } catch (err) {
        errBox.classList.remove('d-none');
    }
}

// ── Edit Profile ─────────────────────────────────────────
async function openEditProfile() {
    const cid = localStorage.getItem('smartmart_customer_id');
    try {
        const res = await fetch(`/api/customers/${cid}`);
        // This hits the phone-lookup route but we need direct customer data
        // Use the portal data we already have
        document.getElementById('ep_name').value = currentCustomer.name || '';
        document.getElementById('ep_phone').value = '';
        document.getElementById('ep_email').value = '';
        document.getElementById('ep_error').classList.add('d-none');
        document.getElementById('ep_success').classList.add('d-none');

        // Try to get full customer data for phone/email
        const allRes = await fetch('/api/customers');
        if (allRes.ok) {
            const allCusts = await allRes.json();
            const me = allCusts.find(c => c.customer_id == cid);
            if (me) {
                document.getElementById('ep_name').value = me.name;
                document.getElementById('ep_phone').value = me.phone || '';
                document.getElementById('ep_email').value = me.email || '';
            }
        }
    } catch (e) { console.error(e); }
    new bootstrap.Modal(document.getElementById('editProfileModal')).show();
}

async function saveProfile() {
    const cid = localStorage.getItem('smartmart_customer_id');
    const payload = {
        name: document.getElementById('ep_name').value.trim(),
        phone: document.getElementById('ep_phone').value.trim(),
        email: document.getElementById('ep_email').value.trim()
    };
    if (!payload.name || !payload.phone || !payload.email) {
        document.getElementById('ep_error').textContent = 'All fields are required.';
        document.getElementById('ep_error').classList.remove('d-none'); return;
    }
    try {
        const res = await fetch(`/api/customers/${cid}`, {
            method: 'PUT', headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(payload)
        });
        const data = await res.json();
        if (res.ok) {
            document.getElementById('ep_success').textContent = 'Profile updated successfully!';
            document.getElementById('ep_success').classList.remove('d-none');
            document.getElementById('ep_error').classList.add('d-none');
            // Update the displayed name
            document.getElementById('cName').innerText = payload.name;
            currentCustomer.name = payload.name;
            setTimeout(() => {
                bootstrap.Modal.getInstance(document.getElementById('editProfileModal')).hide();
            }, 1200);
        } else {
            document.getElementById('ep_error').textContent = data.error;
            document.getElementById('ep_error').classList.remove('d-none');
        }
    } catch (e) {
        document.getElementById('ep_error').textContent = 'Error: ' + e.message;
        document.getElementById('ep_error').classList.remove('d-none');
    }
}

// ── Logout ───────────────────────────────────────────────
function logout() {
    localStorage.removeItem('smartmart_customer_id');
    currentCustomer = null;
    document.getElementById('customerId').value = '';
    document.getElementById('loginPanel').style.display = 'flex';
    document.getElementById('portalPanel').style.display = 'none';
    document.getElementById('navActions').style.display = 'none';
}
