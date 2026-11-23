/* ══════════════════════════════════════════════════════════════════════════════
   App Module — Campus Booking System
   ══════════════════════════════════════════════════════════════════════════════ */

(function () {
    'use strict';

    // ── State ────────────────────────────────────────────────────────────────
    let currentUser = null;
    let selectedDate = todayStr();
    let activeTab = 'resources';

    // ── Helpers ──────────────────────────────────────────────────────────────
    function todayStr() {
        return new Date().toISOString().split('T')[0];
    }

    function formatTime(t) {
        // "HH:MM:SS" or "HH:MM" → "H:MM AM/PM"
        const [h, m] = t.split(':').map(Number);
        const ampm = h >= 12 ? 'PM' : 'AM';
        const h12 = h % 12 || 12;
        return `${h12}:${m.toString().padStart(2, '0')} ${ampm}`;
    }

    function formatDate(d) {
        return new Date(d + 'T00:00:00').toLocaleDateString('en-US', {
            weekday: 'short', month: 'short', day: 'numeric', year: 'numeric'
        });
    }

    function $(sel) { return document.querySelector(sel); }
    function $$(sel) { return document.querySelectorAll(sel); }

    // ── Toast ────────────────────────────────────────────────────────────────
    function toast(message, type = 'info') {
        const container = $('#toast-container');
        const el = document.createElement('div');
        el.className = `toast toast-${type}`;
        el.textContent = message;
        container.appendChild(el);
        setTimeout(() => { el.remove(); }, 3500);
    }

    // ── View Management ──────────────────────────────────────────────────────
    function showAuth() {
        $('#auth-section').classList.remove('hidden');
        $('#app-section').classList.add('hidden');
    }

    function showApp() {
        $('#auth-section').classList.add('hidden');
        $('#app-section').classList.remove('hidden');
        updateNavUser();
        updateAdminVisibility();
        switchTab('resources');
    }

    function updateNavUser() {
        if (!currentUser) return;
        const roleBadge = currentUser.role === 'admin' ? '🛡️ Admin' : '🎓 Student';
        $('#nav-user-info').innerHTML = `${roleBadge} &mdash; <strong>${currentUser.name}</strong>`;
    }

    function updateAdminVisibility() {
        const isAdmin = currentUser && currentUser.role === 'admin';
        const adminTab = $('#tab-admin');
        if (isAdmin) {
            adminTab.classList.remove('hidden');
        } else {
            adminTab.classList.add('hidden');
        }
    }

    function switchTab(tab) {
        activeTab = tab;
        $$('.nav-tab').forEach(t => t.classList.remove('active'));
        const tabEl = $(`#tab-${tab}`);
        if (tabEl) tabEl.classList.add('active');

        $$('.tab-content').forEach(s => s.classList.add('hidden'));
        $(`#content-${tab}`).classList.remove('hidden');

        if (tab === 'resources') loadResources();
        if (tab === 'bookings') loadMyBookings();
        if (tab === 'admin') loadAdminPanel();
    }

    // ── Auth ─────────────────────────────────────────────────────────────────
    function setupAuth() {
        // Tab switching
        $$('.auth-tab').forEach(tab => {
            tab.addEventListener('click', () => {
                $$('.auth-tab').forEach(t => t.classList.remove('active'));
                tab.classList.add('active');
                const target = tab.dataset.tab;
                $$('.auth-form').forEach(f => f.classList.add('hidden'));
                $(`#${target}-form`).classList.remove('hidden');
            });
        });

        // Quick fill
        $('#qf-admin').addEventListener('click', () => {
            $('#login-email').value = 'admin@campus.edu';
            $('#login-password').value = 'admin123';
        });
        $('#qf-student').addEventListener('click', () => {
            $('#login-email').value = 'student1@campus.edu';
            $('#login-password').value = 'student123';
        });

        // Login
        $('#login-form').addEventListener('submit', async (e) => {
            e.preventDefault();
            const email = $('#login-email').value.trim();
            const password = $('#login-password').value;
            try {
                const data = await API.login(email, password);
                API.setToken(data.access_token);
                await loadUser();
                showApp();
                toast('Welcome back!', 'success');
            } catch (err) {
                toast(err.message, 'error');
            }
        });

        // Register
        $('#register-form').addEventListener('submit', async (e) => {
            e.preventDefault();
            const payload = {
                name: $('#reg-name').value.trim(),
                email: $('#reg-email').value.trim(),
                password: $('#reg-password').value,
                role: 'student',
                roll_number: $('#reg-roll').value.trim() || null,
            };
            try {
                const data = await API.register(payload);
                API.setToken(data.access_token);
                await loadUser();
                showApp();
                toast('Account created!', 'success');
            } catch (err) {
                toast(err.message, 'error');
            }
        });

        // Logout
        $('#btn-logout').addEventListener('click', () => {
            API.clearToken();
            currentUser = null;
            showAuth();
            toast('Logged out', 'info');
        });
    }

    async function loadUser() {
        currentUser = await API.getMe();
    }

    // ── Resources ────────────────────────────────────────────────────────────
    function setupResourceFilters() {
        $('#filter-date').value = selectedDate;
        $('#filter-type').addEventListener('change', loadResources);
        $('#filter-capacity').addEventListener('change', loadResources);
        $('#filter-date').addEventListener('change', (e) => {
            selectedDate = e.target.value;
            loadResources();
        });
    }

    async function loadResources() {
        const type = $('#filter-type').value;
        const min_capacity = $('#filter-capacity').value || undefined;
        const grid = $('#resource-grid');
        grid.innerHTML = '<div class="loading"><div class="spinner"></div> Loading resources...</div>';

        try {
            const resources = await API.getResources({ type, min_capacity });
            if (resources.length === 0) {
                grid.innerHTML = `
                    <div class="empty-state" style="grid-column: 1/-1;">
                        <div class="empty-state-icon">📚</div>
                        <p>No resources match your filters.</p>
                    </div>`;
                return;
            }
            grid.innerHTML = resources.map(r => renderResourceCard(r)).join('');
        } catch (err) {
            grid.innerHTML = `<p class="text-center text-secondary">Failed to load resources.</p>`;
            toast(err.message, 'error');
        }
    }

    function renderResourceCard(r) {
        let tags = [];
        try { tags = JSON.parse(r.equipment_tags || '[]'); } catch (e) {}
        const typeLabel = r.type === 'study_room' ? 'Study Room' : 'Lab';
        return `
        <div class="card resource-card">
            <div class="card-header">
                <div>
                    <h3>${esc(r.name)}</h3>
                    <span class="resource-type-badge type-${r.type}">${typeLabel}</span>
                </div>
            </div>
            <div class="card-body">
                <div class="resource-info">
                    <div class="resource-info-row">👥 Capacity: <strong>${r.capacity}</strong></div>
                    <div class="resource-info-row">📍 ${esc(r.location)}</div>
                </div>
                <div class="equipment-tags">
                    ${tags.map(t => `<span class="equipment-tag">${esc(t)}</span>`).join('')}
                </div>
                <div class="slot-grid-container" id="slots-${r.id}"></div>
            </div>
            <div class="card-footer">
                <button class="btn btn-primary btn-sm" onclick="App.viewSlots(${r.id}, '${esc(r.name)}')">
                    📅 View Slots
                </button>
            </div>
        </div>`;
    }

    async function viewSlots(resourceId, resourceName) {
        const container = $(`#slots-${resourceId}`);
        container.innerHTML = '<div class="loading"><div class="spinner"></div> Loading...</div>';

        try {
            const data = await API.getAvailability(resourceId, selectedDate);
            container.innerHTML = renderSlotGrid(data, resourceId, resourceName);
        } catch (err) {
            container.innerHTML = `<p class="form-error">${err.message}</p>`;
        }
    }

    function renderSlotGrid(data, resourceId, resourceName) {
        const slots = data.slots;
        const slotHtml = slots.map(s => {
            const startH = parseInt(s.start_time.split(':')[0]);
            const endH = parseInt(s.end_time.split(':')[0]);
            const timeStr = `${formatTime(s.start_time)} – ${formatTime(s.end_time)}`;
            let cls = 'slot-available';
            let label = 'Available';
            let clickAttr = '';

            if (s.status === 'blocked') {
                cls = 'slot-blocked';
                label = `🔒 ${s.purpose || 'Blocked'}`;
            } else if (s.status === 'confirmed') {
                if (currentUser && s.user_name === currentUser.name) {
                    cls = 'slot-mine';
                    label = '📌 Your Booking';
                } else {
                    cls = 'slot-confirmed';
                    label = `Booked`;
                }
            }

            if (s.status === 'available') {
                clickAttr = `onclick="App.openBookingModal(${resourceId}, '${esc(resourceName)}', '${selectedDate}', '${s.start_time}', '${s.end_time}')"`;
            }

            return `<div class="slot ${cls}" ${clickAttr}>
                <div class="slot-time">${timeStr}</div>
                <div class="slot-label">${label}</div>
            </div>`;
        }).join('');

        return `
            <div class="slot-grid-title">📅 ${formatDate(selectedDate)}</div>
            <div class="slot-grid">${slotHtml}</div>
            <div class="slot-legend">
                <div class="legend-item"><div class="legend-dot available"></div> Available</div>
                <div class="legend-item"><div class="legend-dot booked"></div> Booked</div>
                <div class="legend-item"><div class="legend-dot mine"></div> Your Booking</div>
                <div class="legend-item"><div class="legend-dot blocked"></div> Blocked</div>
            </div>`;
    }

    // ── Booking Modal ────────────────────────────────────────────────────────
    function openBookingModal(resourceId, resourceName, date, startTime, endTime) {
        const startH = parseInt(startTime.split(':')[0]);
        // Build end-time options (1 or 2 hours)
        let endOptions = `<option value="${pad(startH + 1)}:00:00">${formatTime(pad(startH + 1) + ':00')}</option>`;
        if (startH + 2 <= 20) {
            endOptions += `<option value="${pad(startH + 2)}:00:00">${formatTime(pad(startH + 2) + ':00')} (2 hours)</option>`;
        }

        $('#modal-container').innerHTML = `
        <div class="modal-overlay" onclick="App.closeModal(event)">
            <div class="modal" onclick="event.stopPropagation()">
                <div class="modal-header">
                    <h3>📝 Book Slot</h3>
                    <button class="modal-close" onclick="App.closeModal()">&times;</button>
                </div>
                <div class="modal-body">
                    <div class="form-group">
                        <label>Resource</label>
                        <input class="form-control" value="${esc(resourceName)}" disabled>
                    </div>
                    <div class="form-row">
                        <div class="form-group">
                            <label>Date</label>
                            <input class="form-control" value="${date}" disabled>
                        </div>
                        <div class="form-group">
                            <label>Start Time</label>
                            <input class="form-control" value="${formatTime(startTime)}" disabled>
                        </div>
                    </div>
                    <div class="form-group">
                        <label>End Time</label>
                        <select class="form-control" id="modal-end-time">${endOptions}</select>
                    </div>
                    <div class="form-group">
                        <label>Purpose</label>
                        <textarea class="form-control" id="modal-purpose" placeholder="e.g., Group study session, Lab exercise..."></textarea>
                    </div>
                </div>
                <div class="modal-footer">
                    <button class="btn btn-outline" onclick="App.closeModal()">Cancel</button>
                    <button class="btn btn-success" id="modal-confirm" onclick="App.confirmBooking(${resourceId}, '${date}', '${startTime}')">
                        ✅ Confirm Booking
                    </button>
                </div>
            </div>
        </div>`;
    }

    function closeModal(event) {
        if (event && event.target !== event.currentTarget) return;
        $('#modal-container').innerHTML = '';
    }

    async function confirmBooking(resourceId, date, startTime) {
        const endTime = $('#modal-end-time').value;
        const purpose = $('#modal-purpose').value.trim();
        const btn = $('#modal-confirm');
        btn.disabled = true;
        btn.textContent = 'Booking...';

        try {
            await API.createBooking({
                resource_id: resourceId,
                booking_date: date,
                start_time: startTime,
                end_time: endTime,
                purpose: purpose || 'General use',
            });
            closeModal();
            toast('Booking confirmed! 🎉', 'success');
            viewSlots(resourceId, '');
        } catch (err) {
            toast(err.message, 'error');
            btn.disabled = false;
            btn.textContent = '✅ Confirm Booking';
        }
    }

    function pad(n) { return n.toString().padStart(2, '0'); }

    // ── My Bookings ──────────────────────────────────────────────────────────
    async function loadMyBookings() {
        const container = $('#my-bookings-list');
        container.innerHTML = '<div class="loading"><div class="spinner"></div> Loading bookings...</div>';

        try {
            const bookings = await API.getMyBookings();
            if (bookings.length === 0) {
                container.innerHTML = `
                    <div class="empty-state">
                        <div class="empty-state-icon">📋</div>
                        <p>You have no bookings yet. Head to Resources to book a slot!</p>
                    </div>`;
                return;
            }
            container.innerHTML = `<div class="booking-list">${bookings.map(b => renderBookingItem(b)).join('')}</div>`;
        } catch (err) {
            container.innerHTML = `<p class="text-center text-secondary">Failed to load bookings.</p>`;
        }
    }

    function renderBookingItem(b) {
        const today = todayStr();
        const canCancel = b.status === 'confirmed' && b.booking_date >= today;
        const cancelBtn = canCancel
            ? `<button class="btn btn-danger btn-sm" onclick="App.cancelBooking(${b.id})">Cancel</button>`
            : '';

        return `
        <div class="booking-item">
            <div class="booking-info">
                <div class="booking-resource">${esc(b.resource_name || 'Resource #' + b.resource_id)}</div>
                <div class="booking-details">
                    📅 ${formatDate(b.booking_date)} &nbsp;|&nbsp;
                    🕐 ${formatTime(b.start_time)} – ${formatTime(b.end_time)}
                    ${b.purpose ? ` &nbsp;|&nbsp; 📝 ${esc(b.purpose)}` : ''}
                </div>
            </div>
            <div class="booking-actions">
                <span class="status-badge status-${b.status}">${b.status}</span>
                ${cancelBtn}
            </div>
        </div>`;
    }

    async function cancelBooking(id) {
        if (!confirm('Are you sure you want to cancel this booking?')) return;
        try {
            await API.cancelBooking(id);
            toast('Booking cancelled', 'success');
            loadMyBookings();
        } catch (err) {
            toast(err.message, 'error');
        }
    }

    // ── Admin Panel ──────────────────────────────────────────────────────────
    async function loadAdminPanel() {
        loadAdminResources();
        loadAllBookings();
        setupBlockSlotForm();
    }

    async function loadAdminResources() {
        const container = $('#admin-resources-body');
        try {
            const resources = await API.getResources({ is_active: undefined });
            // Fetch all including inactive
            const allResources = await API.request('GET', '/resources?is_active=true');
            const inactiveResources = await API.request('GET', '/resources?is_active=false').catch(() => []);
            const all = [...allResources, ...inactiveResources];

            container.innerHTML = all.map(r => `
                <tr>
                    <td><strong>${esc(r.name)}</strong></td>
                    <td><span class="resource-type-badge type-${r.type}">${r.type === 'study_room' ? 'Study Room' : 'Lab'}</span></td>
                    <td>${r.capacity}</td>
                    <td>${esc(r.location)}</td>
                    <td>
                        <span class="${r.is_active ? 'toggle-active' : 'toggle-inactive'}">
                            ${r.is_active ? '● Active' : '○ Inactive'}
                        </span>
                    </td>
                    <td>
                        <button class="btn btn-outline btn-sm" onclick="App.toggleResource(${r.id})">
                            ${r.is_active ? 'Deactivate' : 'Activate'}
                        </button>
                    </td>
                </tr>`).join('');
        } catch (err) {
            container.innerHTML = `<tr><td colspan="6" class="text-center">Failed to load</td></tr>`;
        }
    }

    async function toggleResource(id) {
        try {
            await API.toggleResource(id);
            toast('Resource status updated', 'success');
            loadAdminResources();
            loadResources();
        } catch (err) {
            toast(err.message, 'error');
        }
    }

    function setupAddResourceForm() {
        $('#add-resource-form').addEventListener('submit', async (e) => {
            e.preventDefault();
            const tags = $('#ar-tags').value.split(',').map(t => t.trim()).filter(Boolean);
            try {
                await API.createResource({
                    name: $('#ar-name').value.trim(),
                    type: $('#ar-type').value,
                    capacity: parseInt($('#ar-capacity').value),
                    location: $('#ar-location').value.trim(),
                    equipment_tags: tags,
                });
                toast('Resource created!', 'success');
                e.target.reset();
                loadAdminResources();
                loadResources();
            } catch (err) {
                toast(err.message, 'error');
            }
        });
    }

    function setupBlockSlotForm() {
        // Populate resource select
        API.getResources({}).then(resources => {
            const sel = $('#block-resource');
            sel.innerHTML = resources.map(r =>
                `<option value="${r.id}">${esc(r.name)}</option>`
            ).join('');
        });

        if (!$('#block-slot-form').dataset.bound) {
            $('#block-slot-form').dataset.bound = 'true';
            $('#block-slot-form').addEventListener('submit', async (e) => {
                e.preventDefault();
                try {
                    await API.blockSlot({
                        resource_id: parseInt($('#block-resource').value),
                        booking_date: $('#block-date').value,
                        start_time: $('#block-start').value + ':00',
                        end_time: $('#block-end').value + ':00',
                        purpose: $('#block-purpose').value.trim() || 'Maintenance',
                    });
                    toast('Slot blocked!', 'success');
                    e.target.reset();
                    loadAllBookings();
                } catch (err) {
                    toast(err.message, 'error');
                }
            });
        }
    }

    async function loadAllBookings() {
        const container = $('#admin-bookings-body');
        try {
            const bookings = await API.getAllBookings({});
            container.innerHTML = bookings.map(b => `
                <tr>
                    <td>${esc(b.resource_name || '')}</td>
                    <td>${esc(b.user_name || '')}</td>
                    <td>${formatDate(b.booking_date)}</td>
                    <td>${formatTime(b.start_time)} – ${formatTime(b.end_time)}</td>
                    <td>${esc(b.purpose || '-')}</td>
                    <td><span class="status-badge status-${b.status}">${b.status}</span></td>
                    <td>
                        ${b.status !== 'cancelled' ? `<button class="btn btn-ghost btn-sm" onclick="App.adminCancel(${b.id})">✕</button>` : ''}
                    </td>
                </tr>`).join('') || '<tr><td colspan="7" class="text-center">No bookings found</td></tr>';
        } catch (err) {
            container.innerHTML = `<tr><td colspan="7" class="text-center">Failed to load</td></tr>`;
        }
    }

    async function adminCancel(id) {
        if (!confirm('Cancel this booking?')) return;
        try {
            await API.adminCancelBooking(id);
            toast('Booking cancelled by admin', 'success');
            loadAllBookings();
        } catch (err) {
            toast(err.message, 'error');
        }
    }

    // ── Escape HTML ──────────────────────────────────────────────────────────
    function esc(str) {
        const div = document.createElement('div');
        div.textContent = str || '';
        return div.innerHTML;
    }

    // ── Navigation Setup ─────────────────────────────────────────────────────
    function setupNav() {
        $$('.nav-tab').forEach(tab => {
            tab.addEventListener('click', () => {
                const target = tab.dataset.tab;
                if (target) switchTab(target);
            });
        });
    }

    // ── Init ─────────────────────────────────────────────────────────────────
    async function init() {
        setupAuth();
        setupNav();
        setupResourceFilters();
        setupAddResourceForm();

        // Check existing token
        if (API.getToken()) {
            try {
                await loadUser();
                showApp();
            } catch {
                API.clearToken();
                showAuth();
            }
        } else {
            showAuth();
        }
    }

    // ── Public API (called from inline onclick handlers) ─────────────────────
    window.App = {
        viewSlots,
        openBookingModal,
        closeModal,
        confirmBooking,
        cancelBooking,
        toggleResource,
        adminCancel,
    };

    // ── Boot ─────────────────────────────────────────────────────────────────
    document.addEventListener('DOMContentLoaded', init);
})();
