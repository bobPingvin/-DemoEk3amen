let allOrders = [];
let pickupPoints = [];
let currentOrderId = null;

document.addEventListener('DOMContentLoaded', async () => {
  Auth.initHeader();
  const user = Auth.get();
  if (user.role !== 'Менеджер' && user.role !== 'Администратор') {
    alert('Доступ запрещен');
    location.href = 'index.html';
    return;
  }

  if (user.role === 'Администратор') {
    document.getElementById('btn-add-order').style.display = 'block';
  }

  const metaRes = await fetch('/api/meta');
  const meta = await metaRes.json();
  pickupPoints = meta.pickup_points;

  document.getElementById('order-point').innerHTML = pickupPoints
    .map(p => `<option value="${p.ID}">${p.Address}</option>`)
    .join('');

  loadOrders();
});

async function loadOrders() {
  const r = await fetch('/api/orders');
  allOrders = await r.json();
  const container = document.getElementById('orders-list');
  const user = Auth.get();

  if (!allOrders.length) {
    container.innerHTML = '<p style="padding:20px;text-align:center;">Заказов нет</p>';
    return;
  }

  container.innerHTML = allOrders.map(o => {
    const clickHandler = user.role === 'Администратор' ? `onclick="openOrderModal(${o.ID})"` : '';
    return `
      <div class="product-row" style="grid-template-columns: 1fr 1fr 1fr;" ${clickHandler}>
        <div>
          <h3>Заказ: ${o.Article}</h3>
          <p><b>Статус:</b> ${o.Status}</p>
        </div>
        <div>
          <p><b>Адрес ПВЗ:</b> ${o.PickupAddress}</p>
        </div>
        <div>
          <p>📅 <b>Заказ:</b> ${o.OrderDate}</p>
          <p>🚚 <b>Выдача:</b> ${o.DeliveryDate}</p>
        </div>
      </div>
    `;
  }).join('');
}

function openOrderModal(id = null) {
  currentOrderId = id;
  const modal = document.getElementById('order-modal');
  const form = document.getElementById('order-form');
  form.reset();

  const btnDel = document.getElementById('btn-del-order');

  if (id) {
    document.getElementById('order-modal-title').textContent = 'Редактирование заказа';
    btnDel.style.display = 'inline-block';
    const o = allOrders.find(x => x.ID === id);
    if (o) {
      document.getElementById('order-id').value = o.ID;
      document.getElementById('order-article').value = o.Article;
      document.getElementById('order-status').value = o.Status;
      document.getElementById('order-point').value = o.PickupPointID;
      document.getElementById('order-date').value = o.OrderDate;
      document.getElementById('order-delivery').value = o.DeliveryDate;
    }
  } else {
    document.getElementById('order-modal-title').textContent = 'Добавление заказа';
    btnDel.style.display = 'none';
    document.getElementById('order-id').value = '';
  }
  modal.classList.remove('hidden');
}

function closeOrderModal() {
  document.getElementById('order-modal').classList.add('hidden');
  currentOrderId = null;
}

async function saveOrder(e) {
  e.preventDefault();
  const idVal = document.getElementById('order-id').value;
  const payload = {
    id: idVal ? parseInt(idVal) : null,
    article: document.getElementById('order-article').value,
    status: document.getElementById('order-status').value,
    pickup_point_id: parseInt(document.getElementById('order-point').value),
    order_date: document.getElementById('order-date').value,
    delivery_date: document.getElementById('order-delivery').value,
  };

  const r = await fetch('/api/orders', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });

  if (!r.ok) {
    const err = await r.json();
    alert('Ошибка: ' + (err.detail || 'Не удалось сохранить'));
    return;
  }

  closeOrderModal();
  loadOrders();
}

async function deleteCurrentOrder() {
  if (!confirm('Удалить данный заказ?')) return;
  const r = await fetch(`/api/orders/${currentOrderId}`, { method: 'DELETE' });
  if (!r.ok) {
    alert('Ошибка удаления');
    return;
  }
  closeOrderModal();
  loadOrders();
}