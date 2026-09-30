const API = '';

async function loadDirections() {
  const r = await fetch(`${API}/api/shop/directions`);
  const dirs = await r.json();
  const sel = document.getElementById('filter-direction');
  dirs.forEach(d => {
    const opt = document.createElement('option');
    opt.value = d.ID;
    opt.textContent = d.Title;
    sel.appendChild(opt);
  });
}

async function loadEvents() {
  const search = document.getElementById('search').value.trim();
  const dirId  = document.getElementById('filter-direction').value;
  const params = new URLSearchParams();
  if (search) params.append('search', search);
  if (dirId)  params.append('direction_id', dirId);

  const status = document.getElementById('status');
  status.textContent = 'Загрузка...';

  const r = await fetch(`${API}/api/shop/events?${params}`);
  const events = await r.json();
  const box = document.getElementById('events');

  if (!events.length) {
    box.innerHTML = '';
    status.textContent = 'Ничего не найдено';
    return;
  }

  status.textContent = `${events.length} мероприятий`;

  box.innerHTML = events.map(e => `
    <div class="card" onclick="location.href='event.html?id=${e.ID}'">
      <div class="card-head">
        <span class="badge">${e.DirectionTitle || '—'}</span>
        <span class="price">${e.Price} ₽</span>
      </div>
      <h3>${escapeHtml(e.Title)}</h3>
      <p class="meta">📍 ${escapeHtml(e.CityName || '—')}</p>
      <p class="meta">📅 ${e.StartDate} · ${e.Days} дн.</p>
      <button class="btn-buy" onclick="event.stopPropagation(); quickBuy(${e.ID})">
        🛒 В корзину
      </button>
    </div>
  `).join('');
}

function quickBuy(eventId) {
  // Быстрое добавление в корзину
  fetch(`${API}/api/shop/events/${eventId}`)
    .then(r => r.json())
    .then(e => {
      Cart.add({
        event_id: e.ID,
        title: e.Title,
        price: e.Price,
        quantity: 1,
      });
      alert('Добавлено в корзину');
    });
}

function escapeHtml(s) {
  return String(s ?? '').replace(/[&<>"']/g, c =>
    ({ '&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;' }[c]));
}

document.getElementById('search').addEventListener('input', debounce(loadEvents, 300));
document.getElementById('filter-direction').addEventListener('change', loadEvents);

function debounce(fn, ms) {
  let t; return (...args) => { clearTimeout(t); t = setTimeout(() => fn(...args), ms); };
}

loadDirections();
loadEvents();