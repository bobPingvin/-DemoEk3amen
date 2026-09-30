const Auth = {
    get() {
      return JSON.parse(sessionStorage.getItem('currentUser')) || { role: 'Гость', fio: 'Гость' };
    },
    set(user) {
      sessionStorage.setItem('currentUser', JSON.stringify(user));
    },
    logout() {
      sessionStorage.clear();
      location.href = 'index.html';
    },
    initHeader() {
      const user = this.get();
      const fioEl = document.getElementById('user-fio');
      if (fioEl) fioEl.textContent = `${user.fio} (${user.role})`;
  
      // Кнопка перехода в "Заказы" только для Менеджера и Админа
      const ordersBtn = document.getElementById('btn-orders');
      if (ordersBtn) {
        if (user.role === 'Менеджер' || user.role === 'Администратор') {
          ordersBtn.style.display = 'inline-block';
        } else {
          ordersBtn.style.display = 'none';
        }
      }
    }
  };