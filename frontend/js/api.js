/* ══════════════════════════════════════════════════════════════════════════════
   API Module — Campus Booking System
   ══════════════════════════════════════════════════════════════════════════════ */

const API = {
    baseUrl: (typeof window !== 'undefined' && window.location.protocol.startsWith('http'))
        ? '/api'
        : 'http://localhost:8000/api',

    getToken() {
        return localStorage.getItem('token');
    },

    setToken(token) {
        localStorage.setItem('token', token);
    },

    clearToken() {
        localStorage.removeItem('token');
    },

    async request(method, path, body = null) {
        const headers = { 'Content-Type': 'application/json' };
        const token = this.getToken();
        if (token) headers['Authorization'] = `Bearer ${token}`;

        const opts = { method, headers };
        if (body) opts.body = JSON.stringify(body);

        const res = await fetch(`${this.baseUrl}${path}`, opts);

        if (res.status === 204) return null;

        const data = await res.json().catch(() => null);

        if (!res.ok) {
            const msg = data?.detail || `Error ${res.status}`;
            const err = new Error(msg);
            err.status = res.status;
            throw err;
        }
        return data;
    },

    // ── Auth ────────────────────────────────────────────────────────────────
    login(email, password) {
        return this.request('POST', '/auth/login', { email, password });
    },
    register(data) {
        return this.request('POST', '/auth/register', data);
    },
    getMe() {
        return this.request('GET', '/auth/me');
    },

    // ── Resources ───────────────────────────────────────────────────────────
    getResources(params = {}) {
        const q = new URLSearchParams();
        if (params.type && params.type !== 'all') q.set('type', params.type);
        if (params.min_capacity) q.set('min_capacity', params.min_capacity);
        const qs = q.toString();
        return this.request('GET', '/resources' + (qs ? '?' + qs : ''));
    },
    getAvailability(id, date) {
        return this.request('GET', `/resources/${id}/availability?date=${date}`);
    },

    // ── Bookings ────────────────────────────────────────────────────────────
    createBooking(data) {
        return this.request('POST', '/bookings', data);
    },
    getMyBookings() {
        return this.request('GET', '/bookings/my');
    },
    cancelBooking(id) {
        return this.request('DELETE', `/bookings/${id}`);
    },

    // ── Admin ───────────────────────────────────────────────────────────────
    createResource(data) {
        return this.request('POST', '/admin/resources', data);
    },
    updateResource(id, data) {
        return this.request('PUT', `/admin/resources/${id}`, data);
    },
    toggleResource(id) {
        return this.request('PATCH', `/admin/resources/${id}/toggle`);
    },
    getAllBookings(params = {}) {
        const q = new URLSearchParams();
        if (params.date) q.set('date', params.date);
        if (params.resource_id) q.set('resource_id', params.resource_id);
        if (params.status) q.set('status', params.status);
        const qs = q.toString();
        return this.request('GET', '/admin/bookings' + (qs ? '?' + qs : ''));
    },
    blockSlot(data) {
        return this.request('POST', '/admin/block-slot', data);
    },
    adminCancelBooking(id) {
        return this.request('DELETE', `/admin/bookings/${id}`);
    },
};
