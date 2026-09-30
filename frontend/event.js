const API = '';
const params = new URLSearchParams(location.search);
const eventId = params.get('id');

let currentEvent = null;

async function loadEvent() {
  const box = document.getElementById('event-detail');
  const r = await fetch(`${API}/api/shop/events/${eventId}`);
  if (!r.ok) { box.innerHTML = '<p>Мероприятие не найдено</p>'; return; }
  currentEvent = await r.json();

  box.innerHTML = `
    <div class="event-header">
      <h2>${escapeHtml(currentEvent.Title)}</h2>
      <p class="meta">📍 ${escapeHtml(currentEvent.CityName || '—')} · 📅 ${currentEvent.StartDate} · ${currentEvent.Days} дн.</p>
      <p class="meta">🏷️ ${escapeHtml(currentEvent.DirectionTitle || '—')}</p>
      <p class="price-big">${currentEvent.Price} ₽ за билет</p>
      <button class="btn-buy" onclick="openBuyModal()">Купить билеты</button>
    </div>

    <h3>Программа</h3>
    <table class="program">
      <thead>
        <tr><th>День</th><th>Время</th><th>Активность</th><th>Модератор</th><th>Жюри</th></tr>
      </thead>
      <tbody>
        ${currentEvent.activities.map(a => `
          <tr>
            <td>${a.Day ?? ''}</td>
            <td>${a.StartTime ?? ''}</td>
            <td>${escapeHtml(a.Title)}</td>
            <td>${escapeHtml(a.Moderator || '')}</td>
            <td>${[a.Jury1,a.Jury2,a.Jury3,a.Jury4,a.Jury5].filter(Boolean).map(escapeHtml).join(', ')}</td>
          </tr>
        `).join('')}
      </tbody>
    </table>
  `;
}

async function openBuyModal() {
  const modal = document.getElementById('buy-modal');
  modal.classList.remove('hidden');

  const sel = document.getElementById('buyer');
  if (!sel.options.length) {
    const r = await fetch(`${API}/api/shop/members`);
    const members = await r.json();
    sel.innerHTML = members.map(m => `<option value="${m.ID}">${escapeHtml(m.FIO)}</option>`).join('');
  }

  const qty = document.getElementById('qty');
  qty.addEventListener('input', updateTotal);
  updateTotal();
}

function updateTotal() {
  const q = parseInt(document.getElementById('qty').value) || 1;
  document.getElementById('total-price').textContent = q * (currentEvent?.Price || 0);
}

document.getElementById('cancel-buy').onclick = () => {
  document.getElementById('buy-modal').classList.add('hidden');
};

document.getElementById('confirm-buy').onclick = async () => {
  const memberId = parseInt(document.getElementById('buyer').value);
  const qty = parseInt(document.getElementById('qty').value);

  const r = await fetch(`${API}/api/shop/orders`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ member_id: memberId, event_id: parseInt(eventId), quantity: qty }),
  });

  if (!r.ok) {
    const err = await r.json().catch(() => ({}));
    alert('Ошибка: ' + (err.detail || r.status));
    return;
  }

  const res = await r.json();
  document.getElementById('buy-modal').classList.add('hidden');
  alert(`Заказ №${res.order_id} оформлен на сумму ${res.total} ₽`);
};

function escapeHtml(s) {
  return String(s ?? '').replace(/[&<>"']/g, c =>
    ({ '&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;' }[c]));
}

if (eventId) loadEvent();