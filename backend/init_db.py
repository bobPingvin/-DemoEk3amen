import hashlib
import os
import secrets
import sqlite3

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, '4444.db')


def hash_password(password: str, salt: str = None) -> str:
    """Генерация безопасного хеша пароля PBKDF2-HMAC-SHA256 (600_000 итераций)."""
    if salt is None:
        salt = secrets.token_hex(16)
    dk = hashlib.pbkdf2_hmac(
        'sha256', password.encode('utf-8'), bytes.fromhex(salt), 600000
    )
    return f'{salt}${dk.hex()}'


def setup_database():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    # 1. Таблица ролей
    cur.execute("""
        CREATE TABLE IF NOT EXISTS Role (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            Title VARCHAR(50) NOT NULL UNIQUE
        )
    """)
    for role_id, role_name in [
        (1, 'Клиент'),
        (2, 'Менеджер'),
        (3, 'Администратор'),
    ]:
        cur.execute(
            'INSERT OR IGNORE INTO Role (ID, Title) VALUES (?, ?)',
            (role_id, role_name),
        )

    # 2. Таблица пользователей системы (User)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS "User" (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            Login VARCHAR(100) NOT NULL UNIQUE,
            PasswordHash VARCHAR(255) NOT NULL,
            LastName VARCHAR(100) NOT NULL,
            FirstName VARCHAR(100) NOT NULL,
            Patronymic VARCHAR(100),
            RoleID INTEGER NOT NULL REFERENCES Role(ID)
        )
    """)

    # 3. Актуализация таблицы Product
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='Product'")
    if not cur.fetchone():
        cur.execute("""
            CREATE TABLE Product (
                ID INTEGER PRIMARY KEY AUTOINCREMENT,
                Title VARCHAR(100) NOT NULL,
                ProductTypeID INTEGER,
                ArticleNumber VARCHAR(50) NOT NULL UNIQUE,
                Description TEXT,
                Image VARCHAR(255),
                MinCostForAgent REAL NOT NULL CHECK(MinCostForAgent >= 0),
                SupplierID INTEGER,
                Manufacturer VARCHAR(100) DEFAULT 'Россия',
                Quantity INTEGER NOT NULL DEFAULT 0 CHECK(Quantity >= 0),
                Discount REAL NOT NULL DEFAULT 0 CHECK(Discount >= 0 AND Discount <= 100),
                Unit VARCHAR(20) NOT NULL DEFAULT 'шт.'
            )
        """)
    else:
        cur.execute('PRAGMA table_info(Product)')
        cols = [r['name'] for r in cur.fetchall()]
        if 'SupplierID' not in cols:
            cur.execute('ALTER TABLE Product ADD COLUMN SupplierID INTEGER')
        if 'Manufacturer' not in cols:
            cur.execute(
                "ALTER TABLE Product ADD COLUMN Manufacturer VARCHAR(100) DEFAULT 'Россия'"
            )
        if 'Quantity' not in cols:
            cur.execute(
                'ALTER TABLE Product ADD COLUMN Quantity INTEGER DEFAULT 10'
            )
        if 'Discount' not in cols:
            cur.execute('ALTER TABLE Product ADD COLUMN Discount REAL DEFAULT 0')
        if 'Unit' not in cols:
            cur.execute(
                "ALTER TABLE Product ADD COLUMN Unit VARCHAR(20) DEFAULT 'шт.'"
            )

    # 4. Справочники ProductType и Supplier
    cur.execute("""
        CREATE TABLE IF NOT EXISTS ProductType (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            Title VARCHAR(100) NOT NULL UNIQUE,
            DefectedPercent REAL NOT NULL DEFAULT 0
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS Supplier (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            Title VARCHAR(150) NOT NULL UNIQUE,
            INN VARCHAR(12) NOT NULL,
            StartDate DATE NOT NULL,
            QualityRating INTEGER,
            SupplierType VARCHAR(50)
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS PickupPoint (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            Address TEXT NOT NULL UNIQUE
        )
    """)

    # 5. Таблица Order
    cur.execute("""
        CREATE TABLE IF NOT EXISTS "Order" (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            Article VARCHAR(50) NOT NULL UNIQUE,
            Status VARCHAR(50) NOT NULL DEFAULT 'Новый',
            PickupPointID INTEGER NOT NULL REFERENCES PickupPoint(ID),
            OrderDate DATE NOT NULL,
            DeliveryDate DATE NOT NULL,
            ProductID INTEGER REFERENCES Product(ID),
            Quantity INTEGER NOT NULL DEFAULT 1 CHECK(Quantity > 0),
            TotalPrice REAL NOT NULL DEFAULT 0 CHECK(TotalPrice >= 0)
        )
    """)

    # Первичное наполнение справочников, если они пусты
    cur.execute('SELECT COUNT(*) as cnt FROM ProductType')
    if cur.fetchone()['cnt'] == 0:
        cur.executemany(
            'INSERT INTO ProductType (Title, DefectedPercent) VALUES (?, ?)',
            [('Обувь', 0.5), ('Одежда', 0.2), ('Спортинвентарь', 0.1)],
        )

    cur.execute('SELECT COUNT(*) as cnt FROM Supplier')
    if cur.fetchone()['cnt'] == 0:
        cur.executemany(
            """INSERT INTO Supplier (Title, INN, StartDate, QualityRating, SupplierType) 
               VALUES (?, ?, ?, ?, ?)""",
            [
                ('ООО "СпортСнаб"', '7701234567', '2021-01-10', 9, 'Оптовый'),
                ('АО "ГлавТекстиль"', '7809876543', '2019-06-15', 8, 'Производитель'),
                ('ИП Соколов А.В.', '5001122334', '2023-03-20', 10, 'Дистрибьютор'),
            ],
        )

    cur.execute('SELECT COUNT(*) as cnt FROM PickupPoint')
    if cur.fetchone()['cnt'] == 0:
        cur.executemany(
            'INSERT INTO PickupPoint (Address) VALUES (?)',
            [
                ('г. Москва, ул. Ленина, д. 15',),
                ('г. Санкт-Петербург, пр. Мира, д. 40',),
                ('г. Казань, ул. Баумана, д. 7',),
            ],
        )

    # Добавление эталонных пользователей системы (без admin/admin)
    initial_users = [
        (
            'admin@shop.ru',
            'AdminSecure2026!',
            'Сидоров',
            'Алексей',
            'Николаевич',
            3,
        ),
        ('manager@shop.ru', 'Manager2026!', 'Петров', 'Петр', 'Сергеевич', 2),
        ('client@shop.ru', 'Client2026!', 'Иванов', 'Иван', 'Иванович', 1),
    ]

    for login, raw_pwd, last, first, patr, role_id in initial_users:
        cur.execute('SELECT ID FROM "User" WHERE Login = ?', (login,))
        if not cur.fetchone():
            pwd_hash = hash_password(raw_pwd)
            cur.execute(
                """
                INSERT INTO "User" (Login, PasswordHash, LastName, FirstName, Patronymic, RoleID)
                VALUES (?, ?, ?, ?, ?, ?)
            """,
                (login, pwd_hash, last, first, patr, role_id),
            )

    # Если в таблице товаров пусто — добавляем базовые образцы
    cur.execute('SELECT COUNT(*) as cnt FROM Product')
    if cur.fetchone()['cnt'] == 0:
        sample_products = [
            (
                'Кроссовки беговые Pro',
                1,
                'A-1001',
                'Легкие кроссовки с амортизацией',
                '',
                4500.0,
                1,
                'Nike',
                15,
                20.0,
                'пар',
            ),  # скидка > 15% (#2E8B57)
            (
                'Футболка компрессионная',
                2,
                'A-1002',
                'Быстросохнущая ткань для тренировок',
                '',
                1800.5,
                2,
                'Adidas',
                0,
                5.0,
                'шт.',
            ),  # остаток 0 (голубой фон)
            (
                'Мяч футбольный Match',
                3,
                'A-1003',
                'Стандарт FIFA Quality',
                '',
                3200.0,
                3,
                'Puma',
                8,
                0.0,
                'шт.',
            ),
        ]
        cur.executemany(
            """
            INSERT INTO Product (Title, ProductTypeID, ArticleNumber, Description, Image, MinCostForAgent, SupplierID, Manufacturer, Quantity, Discount, Unit)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            sample_products,
        )

    # Таблица сессий (токены в памяти/БД)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS UserSession (
            Token VARCHAR(64) PRIMARY KEY,
            UserID INTEGER NOT NULL REFERENCES "User"(ID),
            CreatedAt DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()
    print('Схема базы данных 4444.db успешно проверена и обновлена!')


if __name__ == '__main__':
    setup_database()