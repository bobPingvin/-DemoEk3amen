PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;
CREATE TABLE Role (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            Title VARCHAR(50) NOT NULL UNIQUE
        );
INSERT INTO Role VALUES(1,'Клиент');
INSERT INTO Role VALUES(2,'Менеджер');
INSERT INTO Role VALUES(3,'Администратор');
CREATE TABLE IF NOT EXISTS "User" (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            Login VARCHAR(100) NOT NULL UNIQUE,
            PasswordHash VARCHAR(255) NOT NULL,
            LastName VARCHAR(100) NOT NULL,
            FirstName VARCHAR(100) NOT NULL,
            Patronymic VARCHAR(100),
            RoleID INTEGER NOT NULL REFERENCES Role(ID)
        );
INSERT INTO User VALUES(1,'admin@shop.ru','d0e75300c1b5775b9dddd3c0f12b61af$da7f197fed6b3d166232b293358615b519c4f100c7399d5c22db36e8ec376b69','Сидоров','Алексей','Николаевич',3);
INSERT INTO User VALUES(2,'manager@shop.ru','daa6ddd6a1edf28003537c546c2611d6$9f58017b38900e9eadeabbb42e5a64d48c3f0842d99c8b63f7662762c85064d4','Петров','Петр','Сергеевич',2);
INSERT INTO User VALUES(3,'client@shop.ru','2e4d28add9357f607429734c11053df1$b16608503ff395a6fff479ab8e7e228d2be43c8f87fa37bb7d633f5fb30e2bff','Иванов','Иван','Иванович',1);
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
            );
INSERT INTO Product VALUES(1,'Кроссовки беговые Pro',1,'A-1001','Легкие кроссовки с амортизацией','',4500.0,1,'Nike',15,20.0,'пар');
INSERT INTO Product VALUES(2,'Футболка компрессионная',2,'A-1002','Быстросохнущая ткань для тренировок','',1800.5,2,'Adidas',0,5.0,'шт.');
INSERT INTO Product VALUES(3,'Мяч футбольный Match',3,'A-1003','Стандарт FIFA Quality','',3200.0,3,'Puma',8,0.0,'шт.');
CREATE TABLE ProductType (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            Title VARCHAR(100) NOT NULL UNIQUE,
            DefectedPercent REAL NOT NULL DEFAULT 0
        );
INSERT INTO ProductType VALUES(1,'Обувь',0.5);
INSERT INTO ProductType VALUES(2,'Одежда',0.2000000000000000111);
INSERT INTO ProductType VALUES(3,'Спортинвентарь',0.1000000000000000055);
CREATE TABLE Supplier (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            Title VARCHAR(150) NOT NULL UNIQUE,
            INN VARCHAR(12) NOT NULL,
            StartDate DATE NOT NULL,
            QualityRating INTEGER,
            SupplierType VARCHAR(50)
        );
INSERT INTO Supplier VALUES(1,'ООО "СпортСнаб"','7701234567','2021-01-10',9,'Оптовый');
INSERT INTO Supplier VALUES(2,'АО "ГлавТекстиль"','7809876543','2019-06-15',8,'Производитель');
INSERT INTO Supplier VALUES(3,'ИП Соколов А.В.','5001122334','2023-03-20',10,'Дистрибьютор');
CREATE TABLE PickupPoint (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            Address TEXT NOT NULL UNIQUE
        );
INSERT INTO PickupPoint VALUES(1,'г. Москва, ул. Ленина, д. 15');
INSERT INTO PickupPoint VALUES(2,'г. Санкт-Петербург, пр. Мира, д. 40');
INSERT INTO PickupPoint VALUES(3,'г. Казань, ул. Баумана, д. 7');
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
        );
INSERT INTO "Order" VALUES(1,'4444','Новый',3,'2027-04-04','2027-04-14',NULL,1,0.0);
CREATE TABLE UserSession (
            Token VARCHAR(64) PRIMARY KEY,
            UserID INTEGER NOT NULL REFERENCES "User"(ID),
            CreatedAt DATETIME DEFAULT CURRENT_TIMESTAMP
        );
INSERT INTO sqlite_sequence VALUES('Role',3);
INSERT INTO sqlite_sequence VALUES('ProductType',3);
INSERT INTO sqlite_sequence VALUES('Supplier',3);
INSERT INTO sqlite_sequence VALUES('PickupPoint',3);
INSERT INTO sqlite_sequence VALUES('User',3);
INSERT INTO sqlite_sequence VALUES('Product',3);
INSERT INTO sqlite_sequence VALUES('Order',1);
COMMIT;
