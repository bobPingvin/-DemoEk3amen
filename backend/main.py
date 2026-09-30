import hashlib
import os
import secrets
import sqlite3
from typing import List, Optional
from fastapi import Depends, FastAPI, File, Form, Header, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from PIL import Image, UnidentifiedImageError
from pydantic import BaseModel

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, '4444.db')
UPLOADS_DIR = os.path.join(BASE_DIR, 'uploads')
FRONTEND_DIR = os.path.join(BASE_DIR, '..', 'frontend')

os.makedirs(UPLOADS_DIR, exist_ok=True)

# Гарантируем наличие файла-заглушки picture.png
placeholder_path = os.path.join(UPLOADS_DIR, 'picture.png')
if not os.path.exists(placeholder_path):
    img = Image.new('RGB', (300, 200), color=(220, 225, 230))
    img.save(placeholder_path)

app = FastAPI(title='ИС Управление складом и товарами')

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute('PRAGMA foreign_keys = ON')
    return conn


def verify_password(plain_password: str, stored_hash: str) -> bool:
    try:
        salt, hash_val = stored_hash.split('$')
        dk = hashlib.pbkdf2_hmac(
            'sha256', plain_password.encode('utf-8'), bytes.fromhex(salt), 600000
        )
        return secrets.compare_digest(dk.hex(), hash_val)
    except Exception:
        return False


# ---------------------------------------------------------------------------
# ЗАЩИТА И ПРОВЕРКА РОЛЕЙ (RBAC)
# ---------------------------------------------------------------------------
def get_current_user(authorization: Optional[str] = Header(None)):
    if not authorization or not authorization.startswith('Bearer '):
        return None
    token = authorization.split(' ')[1].strip()
    conn = get_conn()
    try:
        cur = conn.execute(
            """
            SELECT u.ID, u.Login, u.LastName, u.FirstName, u.Patronymic, r.Title as RoleTitle
            FROM UserSession s
            JOIN "User" u ON u.ID = s.UserID
            JOIN Role r ON r.ID = u.RoleID
            WHERE s.Token = ?
        """,
            (token,),
        )
        user = cur.fetchone()
        return dict(user) if user else None
    finally:
        conn.close()


def require_roles(allowed_roles: List[str]):
    def dependency(user=Depends(get_current_user)):
        if not user:
            raise HTTPException(
                status_code=401,
                detail='Требуется авторизация в системе для выполнения данного действия',
            )
        if user['RoleTitle'] not in allowed_roles:
            raise HTTPException(
                status_code=403,
                detail=f'Доступ запрещен: действие доступно только для ролей {", ".join(allowed_roles)}',
            )
        return user

    return dependency


@app.get('/favicon.ico', include_in_schema=False)
def favicon():
    return FileResponse(placeholder_path)


# ---------------------------------------------------------------------------
# АВТОРИЗАЦИЯ
# ---------------------------------------------------------------------------
class LoginRequest(BaseModel):
    login: str
    password: str


@app.post('/api/auth/login')
def login(data: LoginRequest):
    conn = get_conn()
    try:
        cur = conn.execute(
            """
            SELECT u.ID, u.PasswordHash, u.LastName, u.FirstName, u.Patronymic, r.Title as RoleTitle
            FROM "User" u
            JOIN Role r ON r.ID = u.RoleID
            WHERE u.Login = ?
        """,
            (data.login.strip(),),
        )
        user = cur.fetchone()
        if not user or not verify_password(data.password, user['PasswordHash']):
            raise HTTPException(
                status_code=401, detail='Неверный логин или пароль пользователя'
            )

        token = secrets.token_hex(32)
        conn.execute(
            'INSERT INTO UserSession (Token, UserID) VALUES (?, ?)',
            (token, user['ID']),
        )
        conn.commit()

        fio = f"{user['LastName']} {user['FirstName']} {user['Patronymic'] or ''}".strip()
        return {'token': token, 'fio': fio, 'role': user['RoleTitle']}
    finally:
        conn.close()


@app.post('/api/auth/logout')
def logout(user=Depends(get_current_user), authorization: str = Header(None)):
    if authorization and authorization.startswith('Bearer '):
        token = authorization.split(' ')[1].strip()
        conn = get_conn()
        try:
            conn.execute('DELETE FROM UserSession WHERE Token = ?', (token,))
            conn.commit()
        finally:
            conn.close()
    return {'status': 'ok'}


# ---------------------------------------------------------------------------
# МЕТАДАННЫЕ
# ---------------------------------------------------------------------------
@app.get('/api/meta')
def get_meta():
    conn = get_conn()
    try:
        types = [
            dict(r)
            for r in conn.execute(
                'SELECT ID, Title FROM ProductType ORDER BY Title'
            ).fetchall()
        ]
        suppliers = [
            dict(r)
            for r in conn.execute(
                'SELECT ID, Title FROM Supplier ORDER BY Title'
            ).fetchall()
        ]
        points = [
            dict(r)
            for r in conn.execute(
                'SELECT ID, Address FROM PickupPoint ORDER BY Address'
            ).fetchall()
        ]
        return {
            'product_types': types,
            'suppliers': suppliers,
            'pickup_points': points,
        }
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# ТОВАРЫ
# ---------------------------------------------------------------------------
@app.get('/api/products')
def list_products(
    search: str = '',
    supplier_id: Optional[int] = None,
    sort_qty: Optional[str] = None,
):
    conn = get_conn()
    try:
        sql = """
            SELECT p.ID, p.Title, p.ProductTypeID, p.ArticleNumber, p.Description, p.Image,
                   p.MinCostForAgent AS Price,
                   COALESCE(p.Quantity, 0) AS Quantity,
                   COALESCE(p.Discount, 0) AS Discount,
                   COALESCE(p.Unit, 'шт.') AS Unit,
                   COALESCE(p.Manufacturer, 'Не указан') AS Manufacturer,
                   pt.Title AS CategoryTitle,
                   s.Title AS SupplierTitle,
                   s.ID AS SupplierID
            FROM Product p
            LEFT JOIN ProductType pt ON pt.ID = p.ProductTypeID
            LEFT JOIN Supplier s    ON s.ID = p.SupplierID
            WHERE 1=1
        """
        params = []
        if search:
            term = f'%{search.strip()}%'
            sql += """ AND (
                p.Title LIKE ? OR
                p.ArticleNumber LIKE ? OR
                p.Description LIKE ? OR
                pt.Title LIKE ? OR
                s.Title LIKE ? OR
                p.Manufacturer LIKE ?
            )"""
            params.extend([term] * 6)

        if supplier_id:
            sql += ' AND s.ID = ?'
            params.append(supplier_id)

        if sort_qty == 'asc':
            sql += ' ORDER BY p.Quantity ASC'
        elif sort_qty == 'desc':
            sql += ' ORDER BY p.Quantity DESC'
        else:
            sql += ' ORDER BY p.ID DESC'

        cur = conn.execute(sql, params)
        return [dict(r) for r in cur.fetchall()]
    finally:
        conn.close()


def validate_and_save_image(file: UploadFile) -> str:
    """Проверка типа, ограничение до 5 МБ, ресайз до 300х200, безопасное сохранение."""
    allowed_types = ['image/jpeg', 'image/png', 'image/webp']
    if file.content_type not in allowed_types:
        raise HTTPException(
            400,
            f'Недопустимый формат файла {file.content_type}. Разрешены только JPEG, PNG, WEBP.',
        )

    file_bytes = file.file.read()
    if len(file_bytes) > 5 * 1024 * 1024:
        raise HTTPException(
            400, 'Размер изображения превышает допустимый предел 5 МБ.'
        )

    import io

    try:
        image = Image.open(io.BytesIO(file_bytes))
        image.verify()  # Проверка целостности файла изображения
        image = Image.open(io.BytesIO(file_bytes)).convert('RGB')
    except (UnidentifiedImageError, Exception):
        raise HTTPException(
            400,
            'Переданный файл повреждён или не является корректным изображением.',
        )

    # Требование: оптимальный размер 300х200
    resized_img = image.resize((300, 200), Image.Resampling.LANCZOS)
    filename = f'prod_{secrets.token_hex(8)}.jpg'
    safe_path = os.path.join(UPLOADS_DIR, filename)
    resized_img.save(safe_path, 'JPEG', quality=85)
    return filename


@app.post('/api/products')
def save_product(
    id: Optional[int] = Form(None),
    article: str = Form(...),
    title: str = Form(...),
    category_id: int = Form(...),
    manufacturer: str = Form(...),
    supplier_id: int = Form(...),
    price: float = Form(...),
    unit: str = Form('шт.'),
    quantity: int = Form(...),
    discount: float = Form(0.0),
    description: str = Form(''),
    photo: Optional[UploadFile] = File(None),
    current_user=Depends(require_roles(['Администратор'])),
):
    if price < 0:
        raise HTTPException(400, 'Стоимость товара не может быть отрицательной.')
    if quantity < 0:
        raise HTTPException(
            400, 'Количество товара на складе не может быть отрицательным.'
        )
    if not (0 <= discount <= 100):
        raise HTTPException(
            400, 'Размер действующей скидки должен находиться в диапазоне от 0 до 100%.'
        )

    conn = get_conn()
    try:
        cur = conn.cursor()

        # Проверка уникальности артикула
        cur.execute(
            'SELECT ID FROM Product WHERE ArticleNumber = ? AND (? IS NULL OR ID != ?)',
            (article, id, id),
        )
        if cur.fetchone():
            raise HTTPException(
                400, f'Товар с артикулом "{article}" уже существует в системе.'
            )

        new_photo_name = None
        if photo and photo.filename:
            new_photo_name = validate_and_save_image(photo)

        if id is None:
            cur.execute(
                """
                INSERT INTO Product (ArticleNumber, Title, ProductTypeID, Manufacturer, SupplierID,
                                    MinCostForAgent, Unit, Quantity, Discount, Description, Image)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    article,
                    title,
                    category_id,
                    manufacturer,
                    supplier_id,
                    price,
                    unit,
                    quantity,
                    discount,
                    description,
                    new_photo_name or '',
                ),
            )
        else:
            cur.execute('SELECT Image FROM Product WHERE ID = ?', (id,))
            row = cur.fetchone()
            if not row:
                raise HTTPException(404, 'Редактируемый товар не найден.')

            current_img = row['Image']
            if new_photo_name:
                if (
                    current_img
                    and current_img != 'picture.png'
                    and os.path.basename(current_img) == current_img
                ):
                    old_path = os.path.join(UPLOADS_DIR, current_img)
                    if os.path.exists(old_path):
                        try:
                            os.remove(old_path)
                        except OSError:
                            pass
                current_img = new_photo_name

            cur.execute(
                """
                UPDATE Product
                SET ArticleNumber = ?, Title = ?, ProductTypeID = ?, Manufacturer = ?,
                    SupplierID = ?, MinCostForAgent = ?, Unit = ?, Quantity = ?,
                    Discount = ?, Description = ?, Image = ?
                WHERE ID = ?
            """,
                (
                    article,
                    title,
                    category_id,
                    manufacturer,
                    supplier_id,
                    price,
                    unit,
                    quantity,
                    discount,
                    description,
                    current_img,
                    id,
                ),
            )

        conn.commit()
        return {'status': 'ok'}
    finally:
        conn.close()


@app.delete('/api/products/{product_id}')
def delete_product(
    product_id: int, current_user=Depends(require_roles(['Администратор']))
):
    conn = get_conn()
    try:
        # Проверка ТЗ: Товар, который присутствует в заказе, удалить нельзя
        cur = conn.execute(
            'SELECT COUNT(*) as cnt FROM "Order" WHERE ProductID = ?',
            (product_id,),
        )
        if cur.fetchone()['cnt'] > 0:
            raise HTTPException(
                400,
                'Запрещено удалять товар: он фигурирует в оформленных заказах пользователей.',
            )

        cur.execute('SELECT Image FROM Product WHERE ID = ?', (product_id,))
        row = cur.fetchone()
        if not row:
            raise HTTPException(404, 'Товар не найден.')

        img_name = row['Image']
        if (
            img_name
            and img_name != 'picture.png'
            and os.path.basename(img_name) == img_name
        ):
            old_path = os.path.join(UPLOADS_DIR, img_name)
            if os.path.exists(old_path):
                try:
                    os.remove(old_path)
                except OSError:
                    pass

        conn.execute('DELETE FROM Product WHERE ID = ?', (product_id,))
        conn.commit()
        return {'status': 'ok'}
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# ЗАКАЗЫ (Менеджер / Администратор)
# ---------------------------------------------------------------------------
class OrderIn(BaseModel):
    id: Optional[int] = None
    article: str
    status: str
    pickup_point_id: int
    order_date: str
    delivery_date: str
    product_id: Optional[int] = None


@app.get('/api/orders')
def list_orders(
    current_user=Depends(require_roles(['Менеджер', 'Администратор'])),
):
    conn = get_conn()
    try:
        sql = """
            SELECT o.ID, o.Article, o.Status, o.OrderDate, o.DeliveryDate,
                   o.ProductID, o.PickupPointID, p.Address AS PickupAddress,
                   pr.Title AS ProductTitle
            FROM "Order" o
            LEFT JOIN PickupPoint p ON p.ID = o.PickupPointID
            LEFT JOIN Product pr    ON pr.ID = o.ProductID
            ORDER BY o.ID DESC
        """
        cur = conn.execute(sql)
        return [dict(r) for r in cur.fetchall()]
    finally:
        conn.close()


@app.post('/api/orders')
def save_order(
    data: OrderIn,
    current_user=Depends(require_roles(['Администратор'])),
):
    conn = get_conn()
    try:
        cur = conn.cursor()
        if data.id is None:
            cur.execute(
                """
                INSERT INTO "Order" (Article, Status, PickupPointID, OrderDate, DeliveryDate, ProductID)
                VALUES (?, ?, ?, ?, ?, ?)
            """,
                (
                    data.article,
                    data.status,
                    data.pickup_point_id,
                    data.order_date,
                    data.delivery_date,
                    data.product_id,
                ),
            )
        else:
            cur.execute(
                """
                UPDATE "Order"
                SET Article = ?, Status = ?, PickupPointID = ?, OrderDate = ?, DeliveryDate = ?, ProductID = ?
                WHERE ID = ?
            """,
                (
                    data.article,
                    data.status,
                    data.pickup_point_id,
                    data.order_date,
                    data.delivery_date,
                    data.product_id,
                    data.id,
                ),
            )
        conn.commit()
        return {'status': 'ok'}
    finally:
        conn.close()


@app.delete('/api/orders/{order_id}')
def delete_order(
    order_id: int,
    current_user=Depends(require_roles(['Администратор'])),
):
    conn = get_conn()
    try:
        conn.execute('DELETE FROM "Order" WHERE ID = ?', (order_id,))
        conn.commit()
        return {'status': 'ok'}
    finally:
        conn.close()


# Статические каталоги
app.mount('/uploads', StaticFiles(directory=UPLOADS_DIR), name='uploads')
if os.path.isdir(FRONTEND_DIR):
    app.mount('/', StaticFiles(directory=FRONTEND_DIR, html=True), name='static')