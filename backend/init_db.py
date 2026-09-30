import os
import sqlite3

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "shop.db")


def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.executescript(
        """
        PRAGMA foreign_keys = ON;

        CREATE TABLE IF NOT EXISTS Role (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            Title TEXT NOT NULL UNIQUE
        );

        CREATE TABLE IF NOT EXISTS User (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            Login TEXT NOT NULL UNIQUE,
            Password TEXT NOT NULL,
            LastName TEXT NOT NULL,
            FirstName TEXT NOT NULL,
            Patronymic TEXT,
            RoleID INTEGER NOT NULL,
            FOREIGN KEY (RoleID) REFERENCES Role(ID)
        );

        CREATE TABLE IF NOT EXISTS Category (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            Title TEXT NOT NULL UNIQUE
        );

        CREATE TABLE IF NOT EXISTS Manufacturer (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            Title TEXT NOT NULL UNIQUE
        );

        CREATE TABLE IF NOT EXISTS Supplier (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            Title TEXT NOT NULL UNIQUE
        );

        CREATE TABLE IF NOT EXISTS Product (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            Article TEXT UNIQUE,
            Title TEXT NOT NULL,
            CategoryID INTEGER NOT NULL,
            Description TEXT,
            ManufacturerID INTEGER NOT NULL,
            SupplierID INTEGER NOT NULL,
            Price REAL NOT NULL CHECK(Price >= 0),
            Unit TEXT NOT NULL DEFAULT 'шт.',
            Quantity INTEGER NOT NULL CHECK(Quantity >= 0),
            Discount REAL NOT NULL DEFAULT 0 CHECK(Discount >= 0 AND Discount <= 100),
            PhotoPath TEXT,
            FOREIGN KEY (CategoryID) REFERENCES Category(ID),
            FOREIGN KEY (ManufacturerID) REFERENCES Manufacturer(ID),
            FOREIGN KEY (SupplierID) REFERENCES Supplier(ID)
        );

        CREATE TABLE IF NOT EXISTS PickupPoint (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            Address TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS "Order" (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            Article TEXT NOT NULL,
            Status TEXT NOT NULL,
            PickupPointID INTEGER NOT NULL,
            OrderDate TEXT NOT NULL,
            DeliveryDate TEXT NOT NULL,
            FOREIGN KEY (PickupPointID) REFERENCES PickupPoint(ID)
        );

        CREATE TABLE IF NOT EXISTS OrderItem (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            OrderID INTEGER NOT NULL,
            ProductID INTEGER NOT NULL,
            Count INTEGER NOT NULL CHECK(Count > 0),
            FOREIGN KEY (OrderID) REFERENCES "Order"(ID) ON DELETE CASCADE,
            FOREIGN KEY (ProductID) REFERENCES Product(ID)
        );
    """
    )

    # Заполнение ролями
    roles = [(1, "Клиент"), (2, "Менеджер"), (3, "Администратор")]
    cur.executemany("INSERT OR IGNORE INTO Role (ID, Title) VALUES (?, ?)", roles)

    # Тестовые пользователи (логин / пароль)
    users = [
        (1, "client", "123456", "Иванов", "Иван", "Иванович", 1),
        (2, "manager", "123456", "Петров", "Петр", "Сергеевич", 2),
        (3, "admin", "123456", "Сидоров", "Алексей", "Николаевич", 3),
    ]
    cur.executemany(
        """INSERT OR IGNORE INTO User (ID, Login, Password, LastName, FirstName, Patronymic, RoleID)
                       VALUES (?, ?, ?, ?, ?, ?, ?)""",
        users,
    )

    # Справочники
    categories = [(1, "Одежда"), (2, "Обувь"), (3, "Аксессуары")]
    cur.executemany(
        "INSERT OR IGNORE INTO Category (ID, Title) VALUES (?, ?)", categories
    )

    manufacturers = [(1, "Nike"), (2, "Adidas"), (3, "Puma")]
    cur.executemany(
        "INSERT OR IGNORE INTO Manufacturer (ID, Title) VALUES (?, ?)",
        manufacturers,
    )

    suppliers = [(1, "ООО 'СпортСнаб'"), (2, "АО 'ГлавТорг'")]
    cur.executemany(
        "INSERT OR IGNORE INTO Supplier (ID, Title) VALUES (?, ?)", suppliers
    )

    points = [
        (1, "г. Москва, ул. Ленина, д. 10"),
        (2, "г. Санкт-Петербург, пр. Мира, д. 25"),
    ]
    cur.executemany(
        "INSERT OR IGNORE INTO PickupPoint (ID, Address) VALUES (?, ?)", points
    )

    # Тестовые товары (проверка: скидка > 15%, скидка 0..15%, остаток 0)
    products = [
        (
            1,
            "A001",
            "Кроссовки беговые",
            2,
            "Легкие удобные кроссовки",
            1,
            1,
            5500.0,
            "пар",
            12,
            20.0,
            "",
        ),
        (
            2,
            "A002",
            "Футболка спортивная",
            1,
            "Дышащая ткань 100% полиэстер",
            2,
            2,
            1800.50,
            "шт.",
            0,
            5.0,
            "",
        ),
        (
            3,
            "A003",
            "Рюкзак тренировочный",
            3,
            "Вместимость 25 литров",
            3,
            1,
            3200.0,
            "шт.",
            4,
            0.0,
            "",
        ),
    ]
    cur.executemany(
        """INSERT OR IGNORE INTO Product
                       (ID, Article, Title, CategoryID, Description, ManufacturerID, SupplierID, Price, Unit, Quantity, Discount, PhotoPath)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        products,
    )

    # Тестовый заказ для проверки запрета удаления товара, который есть в заказе
    orders = [(1, "ORD-101", "Новый", 1, "2026-03-01", "2026-03-05")]
    cur.executemany(
        """INSERT OR IGNORE INTO "Order" (ID, Article, Status, PickupPointID, OrderDate, DeliveryDate)
                       VALUES (?, ?, ?, ?, ?, ?)""",
        orders,
    )

    order_items = [(1, 1, 1, 1)]  # Заказ 1 содержит Товар 1
    cur.executemany(
        """INSERT OR IGNORE INTO OrderItem (ID, OrderID, ProductID, Count)
                       VALUES (?, ?, ?, ?)""",
        order_items,
    )

    conn.commit()
    conn.close()
    print("База данных shop.db успешно создана!")


if __name__ == "__main__":
    init_db()