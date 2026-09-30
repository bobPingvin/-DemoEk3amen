// Простая сессионная корзина в localStorage.
// Используется как «быстрая память» между страницами.
const Cart = {
    key: 'shop_cart_v1',
  
    read() {
      try { return JSON.parse(localStorage.getItem(this.key)) || []; }
      catch { return []; }
    },
    write(items) {
      localStorage.setItem(this.key, JSON.stringify(items));
      this.updateBadge();
    },
    add(event) {
      const items = this.read();
      const existing = items.find(i => i.event_id === event.event_id);
      if (existing) existing.quantity += event.quantity;
      else items.push(event);
      this.write(items);
    },
    remove(event_id) {
      this.write(this.read().filter(i => i.event_id !== event_id));
    },
    clear() { this.write([]); },
    count() { return this.read().reduce((s, i) => s + i.quantity, 0); },
    updateBadge() {
      const el = document.getElementById('cart-count');
      if (el) el.textContent = this.count();
    }
  };
  
  document.addEventListener('DOMContentLoaded', () => Cart.updateBadge());