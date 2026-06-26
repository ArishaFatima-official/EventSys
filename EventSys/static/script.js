
// SMART EVENT SYSTEM - SHARED JS UTILITIES


// ── TOAST NOTIFICATIONS ──
function showToast(message, type = 'success') {
    let toast = document.getElementById('toast');
    if (!toast) {
        toast = document.createElement('div');
        toast.id = 'toast';
        toast.className = 'toast';
        document.body.appendChild(toast);
    }

    const icons = { success: '✅', error: '❌', info: 'ℹ️', warning: '⚠️' };
    toast.innerHTML = `<span>${icons[type] || '✅'}</span><span>${message}</span>`;
    toast.className = `toast ${type} show`;

    setTimeout(() => {
        toast.classList.remove('show');
    }, 3000);
}

// ── CONFIRM DIALOG ──
let confirmCallback = null;

function showConfirm(message, callback) {
    confirmCallback = callback;
    document.getElementById('confirmMessage').textContent = message;
    document.getElementById('confirmOverlay').classList.add('open');
}

function closeConfirm() {
    document.getElementById('confirmOverlay').classList.remove('open');
    confirmCallback = null;
}

function doConfirm() {
    if (confirmCallback) confirmCallback();
    closeConfirm();
}

// ── MODAL HELPERS ──
function openModal(id) {
    document.getElementById(id).classList.add('open');
}

function closeModal(id) {
    document.getElementById(id).classList.remove('open');
}

// ── SEARCH TABLE ──
function searchTable(inputId, tableId) {
    const input = document.getElementById(inputId);
    const filter = input.value.toLowerCase();
    const table = document.getElementById(tableId);
    const rows = table.getElementsByTagName('tr');

    for (let i = 1; i < rows.length; i++) {
        const text = rows[i].textContent.toLowerCase();
        rows[i].style.display = text.includes(filter) ? '' : 'none';
    }
}

// ── API HELPERS ──
async function apiFetch(url, method = 'GET', body = null) {
    const options = {
        method,
        headers: { 'Content-Type': 'application/json' }
    };
    if (body) options.body = JSON.stringify(body);

    const res = await fetch(url, options);
    return await res.json();
}

// ── CONFIRM OVERLAY HTML (inject on load) ──
document.addEventListener('DOMContentLoaded', () => {
    if (!document.getElementById('confirmOverlay')) {
        const overlay = document.createElement('div');
        overlay.id = 'confirmOverlay';
        overlay.className = 'confirm-overlay';
        overlay.innerHTML = `
            <div class="confirm-box">
                <div class="icon">🗑️</div>
                <h3>Are you sure?</h3>
                <p id="confirmMessage">This action cannot be undone.</p>
                <div class="confirm-buttons">
                    <button class="btn btn-ghost" onclick="closeConfirm()">Cancel</button>
                    <button class="btn btn-primary" onclick="doConfirm()">Confirm</button>
                </div>
            </div>
        `;
        document.body.appendChild(overlay);
    }
});
