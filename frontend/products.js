let meta = { product_types: [], suppliers: [] };
let allProducts = [];
let currentEditingId = null;

// Загрузка справочников при старте
async function loadMeta() {
  try {
    const r = await fetch('/api/meta');
    meta = await r.json();

    // Заполняем фильтр поставщиков в шапке
    const supFilter = document.getElementById('filter-supplier');
    if (supFilter && meta.suppliers) {
      supFilter.innerHTML = '<option value="">Все поставщики</option>' +
        meta.suppliers.map(s => `<option value="${s.ID}">${s.Title}</option>`).join('');
    }
  } catch (err) {
    console.error('Ошибка загрузки метаданных:', err);
  }
}

document.addEventListener('DOMContentLoaded', async () => {
  Auth.initHeader();
  const user = Auth.get();

  if (user.role === 'Администратор') {
    const addBtn = document.getElementById('btn-add-product');
    if (addBtn) addBtn.style.display = 'block';
  }

  await loadMeta();
  loadProducts();
});

async function loadProducts() {
  const search = document.getElementById('search').value.trim();
  const supId = document.getElementById('filter-supplier').value;
  const sortQty = document.getElementById('sort-qty').value;

  const params = new URLSearchParams();
  if (search) params.append('search', search);
  if (supId) params.append('supplier_id', supId);
  if (sortQty) params.append('sort_qty', sortQty);

  const res = await fetch(`/api/products?${params}`);
  allProducts = await res.json();

  const box = document.getElementById('product-list');
  const user = Auth.get();

  if (!allProducts.length) {
    box.innerHTML = '<p style="text-align:center; padding: 20px;">Товары не найдены</p>';
    return;
  }

  box.innerHTML = allProducts.map(p => {
    const isZero = p.Quantity === 0;
    const isHighDiscount = p.Discount > 15;

    let rowClass = 'product-row';
    if (isZero) rowClass += ' out-of-stock';
    else if (isHighDiscount) rowClass += ' discount-high';

    let priceHtml = '';
    if (p.Discount > 0) {
      const finalPrice = (p.Price * (1 - p.Discount / 100)).toFixed(2);
      priceHtml = `<span class="old-price">${p.Price} ₽</span> <span class="final-price">${finalPrice} ₽</span>`;
    } else {
      priceHtml = `<span class="final-price">${p.Price} ₽</span>`;
    }

    const img = p.Image ? `/uploads/${p.Image}` : '/uploads/picture.png';
    const clickHandler = user.role === 'Администратор' ? `onclick="openProductModal(${p.ID})"` : '';

    return `
      <div class="${rowClass}" ${clickHandler}>
        <img class="product-photo" src="${img}" onerror="this.src='/uploads/picture.png'">
        <div class="product-info">
          <h3>${p.Title} (Арт. ${p.ArticleNumber})</h3>
          <p><b>Категория:</b> ${p.CategoryTitle || '—'} | <b>Производитель:</b> ${p.Manufacturer}</p>
          <p><b>Поставщик:</b> ${p.SupplierTitle || '—'}</p>
          <p><b>Описание:</b> ${p.Description || '—'}</p>
        </div>
        <div>
          <p>Цена: ${priceHtml}</p>
          <p>Скидка: <b>${p.Discount}%</b></p>
        </div>
        <div>
          <p><b>Остаток:</b></p>
          <p style="font-size:16px;">${p.Quantity} ${p.Unit}</p>
        </div>
      </div>
    `;
  }).join('');
}

async function openProductModal(id = null) {
  currentEditingId = id;
  const modal = document.getElementById('product-modal');
  const form = document.getElementById('product-form');
  form.reset();

  // Если метаданные еще не загрузились — подгружаем
  if (!meta.product_types || !meta.product_types.length) {
    await loadMeta();
  }

  // Всегда принудительно генерируем <option> перед показом окна
  const catSelect = document.getElementById('prod-category');
  const supSelect = document.getElementById('prod-supplier');

  catSelect.innerHTML = (meta.product_types || [])
    .map(c => `<option value="${c.ID}">${c.Title}</option>`).join('');

  supSelect.innerHTML = (meta.suppliers || [])
    .map(s => `<option value="${s.ID}">${s.Title}</option>`).join('');

  const idGroup = document.getElementById('group-id');
  const btnDel = document.getElementById('btn-del-prod');

  if (id) {
    document.getElementById('modal-title').textContent = 'Редактирование товара';
    idGroup.style.display = 'block';
    btnDel.style.display = 'inline-block';
    document.getElementById('prod-id').value = id;
    document.getElementById('display-id').value = id;

    const p = allProducts.find(x => x.ID === id);
    if (p) {
      document.getElementById('prod-article').value = p.ArticleNumber || '';
      document.getElementById('prod-title').value = p.Title || '';
      document.getElementById('prod-manufacturer').value = p.Manufacturer || '';
      document.getElementById('prod-category').value = p.ProductTypeID || (meta.product_types[0] ? meta.product_types[0].ID : '');
      document.getElementById('prod-supplier').value = p.SupplierID || (meta.suppliers[0] ? meta.suppliers[0].ID : '');
      document.getElementById('prod-price').value = p.Price || 0;
      document.getElementById('prod-unit').value = p.Unit || 'шт.';
      document.getElementById('prod-qty').value = p.Quantity || 0;
      document.getElementById('prod-discount').value = p.Discount || 0;
      document.getElementById('prod-desc').value = p.Description || '';
    }
  } else {
    document.getElementById('modal-title').textContent = 'Добавление товара';
    idGroup.style.display = 'none';
    btnDel.style.display = 'none';
    document.getElementById('prod-id').value = '';
  }

  modal.classList.remove('hidden');
}

function closeProductModal() {
  document.getElementById('product-modal').classList.add('hidden');
  currentEditingId = null;
}

async function saveProduct(e) {
  e.preventDefault();
  const formData = new FormData();
  const id = document.getElementById('prod-id').value;
  if (id) formData.append('id', id);

  formData.append('article', document.getElementById('prod-article').value);
  formData.append('title', document.getElementById('prod-title').value);
  formData.append('category_id', document.getElementById('prod-category').value);
  formData.append('manufacturer', document.getElementById('prod-manufacturer').value);
  formData.append('supplier_id', document.getElementById('prod-supplier').value);
  formData.append('price', document.getElementById('prod-price').value);
  formData.append('unit', document.getElementById('prod-unit').value);
  formData.append('quantity', document.getElementById('prod-qty').value);
  formData.append('discount', document.getElementById('prod-discount').value);
  formData.append('description', document.getElementById('prod-desc').value);

  const fileInput = document.getElementById('prod-photo');
  if (fileInput.files[0]) {
    formData.append('photo', fileInput.files[0]);
  }

  const res = await fetch('/api/products', { method: 'POST', body: formData });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    alert('Предупреждение: ' + (err.detail || 'Ошибка сохранения'));
    return;
  }
  closeProductModal();
  loadProducts();
}

async function deleteCurrentProduct() {
  if (!confirm('Вы уверены, что хотите удалить товар?')) return;
  const res = await fetch(`/api/products/${currentEditingId}`, { method: 'DELETE' });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    alert('Ошибка: ' + (err.detail || 'Не удалось удалить товар'));
    return;
  }
  closeProductModal();
  loadProducts();
}