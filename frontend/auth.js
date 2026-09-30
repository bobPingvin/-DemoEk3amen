const Auth = {
  get() {
    return JSON.parse(sessionStorage.getItem('currentUser')) || { role: 'Гость', fio: 'Гость', token: null };
  },
  set(user) {
    sessionStorage.setItem('currentUser', JSON.stringify(user));
  },
  async logout() {
    const user = this.get();
    if (user.token) {
      try {
        await fetch('/api/auth/logout', {
          method: 'POST',
          headers: { 'Authorization': `Bearer ${user.token}` }
        });
      } catch (e) {}
    }
    sessionStorage.clear();
    location.href = 'index.html';
  },
  getAuthHeaders(customHeaders = {}) {
    const user = this.get();
    const headers = { ...customHeaders };
    if (user.token) {
      headers['Authorization'] = `Bearer ${user.token}`;
    }
    return headers;
  },
  initHeader() {
    const user = this.get();
    const el = document.getElementById('user-fio');
    if (el) el.textContent = `${user.fio} [${user.role}]`;

    const btnOrders = document.getElementById('btn-orders');
    if (btnOrders) {
      if (user.role === 'Менеджер' || user.role === 'Администратор') {
        btnOrders.style.display = 'inline-block';
      } else {
        btnOrders.style.display = 'none';
      }
    }
  }
};