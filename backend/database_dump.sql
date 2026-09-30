PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;
CREATE TABLE AgentType (
  ID      INTEGER PRIMARY KEY AUTOINCREMENT,
  Title   VARCHAR(50)  NOT NULL,
  Image   VARCHAR(100) NULL
);
CREATE TABLE Supplier (
  ID            INTEGER PRIMARY KEY AUTOINCREMENT,
  Title         VARCHAR(150) NOT NULL,
  INN           VARCHAR(12)  NOT NULL,
  StartDate     DATE         NOT NULL,
  QualityRating INTEGER      NULL,
  SupplierType  VARCHAR(20)  NULL
);
INSERT INTO Supplier VALUES(1,'ООО СпортМастер','7700000000','2020-01-01',NULL,NULL);
CREATE TABLE ProductType (
  ID              INTEGER PRIMARY KEY AUTOINCREMENT,
  Title           VARCHAR(50) NOT NULL,
  DefectedPercent REAL        NOT NULL
);
INSERT INTO ProductType VALUES(1,'Обувь',0.0);
INSERT INTO ProductType VALUES(2,'Одежда',0.0);
CREATE TABLE Product (
  ID                     INTEGER PRIMARY KEY AUTOINCREMENT,
  Title                  VARCHAR(100) NOT NULL,
  ProductTypeID          INTEGER      NULL,
  ArticleNumber          VARCHAR(10)  NOT NULL,
  Description            TEXT         NULL,
  Image                  VARCHAR(100) NULL,
  ProductionPersonCount  INTEGER      NULL,
  ProductionWorkshopNumber INTEGER    NULL,
  MinCostForAgent        NUMERIC      NOT NULL, SupplierID INTEGER REFERENCES Supplier(ID), Manufacturer VARCHAR(100) DEFAULT 'Россия', Quantity INTEGER DEFAULT 10, Discount REAL DEFAULT 0, Unit VARCHAR(20) DEFAULT 'шт.',
  FOREIGN KEY (ProductTypeID) REFERENCES ProductType(ID)
    ON DELETE NO ACTION ON UPDATE NO ACTION
);
INSERT INTO Product VALUES(1,'123123',1,'4444','4444','',NULL,NULL,4444,1,'вавап',4,44.0,'шт.');
CREATE TABLE MaterialType (
  ID              INTEGER PRIMARY KEY AUTOINCREMENT,
  Title           VARCHAR(50) NOT NULL,
  DefectedPercent REAL        NOT NULL
);
CREATE TABLE Material (
  ID             INTEGER PRIMARY KEY AUTOINCREMENT,
  Title          VARCHAR(100) NOT NULL,
  CountInPack    INTEGER      NOT NULL,
  Unit           VARCHAR(10)  NOT NULL,
  CountInStock   REAL         NULL,
  MinCount       REAL         NOT NULL,
  Description    TEXT         NULL,
  Cost           NUMERIC      NOT NULL,
  Image          VARCHAR(100) NULL,
  MaterialTypeID INTEGER      NOT NULL,
  FOREIGN KEY (MaterialTypeID) REFERENCES MaterialType(ID)
    ON DELETE NO ACTION ON UPDATE NO ACTION
);
CREATE TABLE MaterialSupplier (
  MaterialID INTEGER NOT NULL,
  SupplierID INTEGER NOT NULL,
  PRIMARY KEY (MaterialID, SupplierID),
  FOREIGN KEY (SupplierID)  REFERENCES Supplier(ID)
    ON DELETE NO ACTION ON UPDATE NO ACTION,
  FOREIGN KEY (MaterialID)  REFERENCES Material(ID)
    ON DELETE NO ACTION ON UPDATE NO ACTION
);
CREATE TABLE ProductMaterial (
  ProductID  INTEGER NOT NULL,
  MaterialID INTEGER NOT NULL,
  Count      REAL    NULL,
  PRIMARY KEY (ProductID, MaterialID),
  FOREIGN KEY (MaterialID) REFERENCES Material(ID)
    ON DELETE NO ACTION ON UPDATE NO ACTION,
  FOREIGN KEY (ProductID)  REFERENCES Product(ID)
    ON DELETE NO ACTION ON UPDATE NO ACTION
);
CREATE TABLE Agent (
  ID          INTEGER PRIMARY KEY AUTOINCREMENT,
  Title       VARCHAR(150) NOT NULL,
  AgentTypeID INTEGER      NOT NULL,
  Address     VARCHAR(300) NULL,
  INN         VARCHAR(12)  NOT NULL,
  KPP         VARCHAR(9)   NULL,
  DirectorName VARCHAR(100) NULL,
  Phone       VARCHAR(20)  NOT NULL,
  Email       VARCHAR(255) NULL,
  Logo        VARCHAR(100) NULL,
  Priority    INTEGER      NOT NULL, "Тип агента;Наименование агента;Электронная почта агента;Телефон агента;Логотип агента;Юридический адрес;Приоритет;Директор;ИНН;КПП" VARCHAR(118),
  FOREIGN KEY (AgentTypeID) REFERENCES AgentType(ID)
    ON DELETE NO ACTION ON UPDATE NO ACTION
);
CREATE TABLE ProductSale (
  ID           INTEGER PRIMARY KEY AUTOINCREMENT,
  AgentID      INTEGER NOT NULL,
  ProductID    INTEGER NOT NULL,
  SaleDate     DATE    NOT NULL,
  ProductCount INTEGER NOT NULL,
  FOREIGN KEY (AgentID)   REFERENCES Agent(ID)
    ON DELETE NO ACTION ON UPDATE NO ACTION,
  FOREIGN KEY (ProductID) REFERENCES Product(ID)
    ON DELETE NO ACTION ON UPDATE NO ACTION
);
CREATE TABLE Shop (
  ID       INTEGER PRIMARY KEY AUTOINCREMENT,
  Title    VARCHAR(150) NOT NULL,
  Address  VARCHAR(300) NULL,
  AgentID  INTEGER      NOT NULL,
  FOREIGN KEY (AgentID) REFERENCES Agent(ID)
    ON DELETE NO ACTION ON UPDATE NO ACTION
);
CREATE TABLE MaterialCountHistory (
  ID          INTEGER PRIMARY KEY AUTOINCREMENT,
  MaterialID  INTEGER NOT NULL,
  ChangeDate  DATETIME NOT NULL,
  CountValue  REAL     NOT NULL,
  FOREIGN KEY (MaterialID) REFERENCES Material(ID)
    ON DELETE NO ACTION ON UPDATE NO ACTION
);
CREATE TABLE ProductCostHistory (
  ID          INTEGER PRIMARY KEY AUTOINCREMENT,
  ProductID   INTEGER NOT NULL,
  ChangeDate  DATETIME NOT NULL,
  CostValue   NUMERIC  NOT NULL,
  FOREIGN KEY (ProductID) REFERENCES Product(ID)
    ON DELETE NO ACTION ON UPDATE NO ACTION
);
CREATE TABLE AgentPriorityHistory (
  ID            INTEGER PRIMARY KEY AUTOINCREMENT,
  AgentID       INTEGER  NOT NULL,
  ChangeDate    DATETIME NOT NULL,
  PriorityValue INTEGER  NOT NULL,
  FOREIGN KEY (AgentID) REFERENCES Agent(ID)
    ON DELETE NO ACTION ON UPDATE NO ACTION
);
CREATE TABLE Country (
  ID            INTEGER PRIMARY KEY AUTOINCREMENT,
  Code2         INTEGER      NOT NULL UNIQUE,   -- числовой код (Код2 из xlsx)
  Name          VARCHAR(100) NOT NULL,          -- русское название
  EnglishName   VARCHAR(100) NULL,              -- English name
  Code          VARCHAR(3)   NOT NULL          -- буквенный код (RU, US, ...)
, "Number;City" VARCHAR(28), "Number" INTEGER, City VARCHAR(25));
CREATE TABLE City (
  ID      INTEGER PRIMARY KEY AUTOINCREMENT,
  Number  INTEGER      NOT NULL UNIQUE,  -- Number из CSV
  Name    VARCHAR(100) NOT NULL          -- City из CSV
);
CREATE TABLE Direction (
  ID    INTEGER PRIMARY KEY AUTOINCREMENT,
  Title VARCHAR(100) NOT NULL UNIQUE
);
INSERT INTO Direction VALUES(1,'ИТ');
INSERT INTO Direction VALUES(2,'Дизайн');
INSERT INTO Direction VALUES(3,'Аналитика');
INSERT INTO Direction VALUES(4,'Биг Дата');
INSERT INTO Direction VALUES(5,'Информационная безопасность');
CREATE TABLE Event (
  ID            INTEGER PRIMARY KEY AUTOINCREMENT,
  Number        INTEGER      NOT NULL,        -- № из xlsx
  Title         VARCHAR(300) NOT NULL,        -- Событие
  StartDate     DATE         NOT NULL,        -- DATE
  Days          INTEGER      NOT NULL,        -- DAYS
  CityID        INTEGER      NULL,            -- FK на City (CityID = числовой код из xlsx)
  DirectionID   INTEGER      NULL,            -- FK на Direction
  FOREIGN KEY (CityID)      REFERENCES City(ID),
  FOREIGN KEY (DirectionID) REFERENCES Direction(ID)
);
INSERT INTO Event VALUES(1,1,'Найди свой трафик 3','2022-03-03',2,NULL,3);
INSERT INTO Event VALUES(2,2,'Найти IT','2022-05-03',3,NULL,1);
INSERT INTO Event VALUES(3,3,'Найти IT Санкт-Петербург','2023-05-20',1,NULL,1);
INSERT INTO Event VALUES(4,4,'Научно-практическая конференция «Разработка ПО/ SECR 2022»','2022-05-21',2,NULL,1);
INSERT INTO Event VALUES(5,5,'Недирективные коммуникации','2022-04-28',3,NULL,3);
INSERT INTO Event VALUES(6,6,'Нейрофизиология предпринимательства. Что происходит в мозгу стартапера?','2022-09-27',1,NULL,3);
INSERT INTO Event VALUES(7,7,'Никогда не ищите работу в геймдеве','2023-05-28',3,NULL,2);
INSERT INTO Event VALUES(8,8,'Новые возможности TrueConf Server 4.3.8, Санкт-Петербург','2022-04-16',2,NULL,4);
INSERT INTO Event VALUES(9,9,'Новые продукты «Лаборатории Касперского» для защиты ИТ-инфраструктуры','2022-12-28',1,NULL,5);
INSERT INTO Event VALUES(10,10,'Новые продукты и решения «Лаборатории Касперского»','2023-12-08',2,NULL,5);
INSERT INTO Event VALUES(11,11,'Новый Яндекс.Директ 2022 года','2022-07-13',3,NULL,4);
INSERT INTO Event VALUES(12,12,'Ночной Питон, Санкт-Петербург','2023-08-23',2,NULL,1);
INSERT INTO Event VALUES(13,13,'Обеспечение информационной безопасности предприятия','2022-02-18',1,NULL,5);
INSERT INTO Event VALUES(14,14,'Облака для критичных систем','2023-06-10',2,NULL,4);
INSERT INTO Event VALUES(15,15,'Облака и реальность: кейсы, грабли, хорошие новости','2022-04-13',2,NULL,4);
INSERT INTO Event VALUES(16,16,'Обработка запросов на изменения. Встреча сообщества аналитиков Петербурга','2022-04-03',3,NULL,3);
INSERT INTO Event VALUES(17,17,'Обучающий курс «IT-рекрутер»','2022-02-18',3,NULL,3);
INSERT INTO Event VALUES(18,18,'Обучающий хакатон «HackCV»','2022-06-23',1,NULL,5);
INSERT INTO Event VALUES(19,19,'Общегородская встреча сообщества HashiCorp User Group#3','2023-06-08',3,NULL,1);
INSERT INTO Event VALUES(20,20,'Общегородская встреча сообщества HashiCorp User Group#5','2023-07-29',2,NULL,1);
CREATE TABLE Jury (
  ID             INTEGER PRIMARY KEY AUTOINCREMENT,
  LastName       VARCHAR(100) NOT NULL,
  FirstName      VARCHAR(100) NOT NULL,
  Patronymic     VARCHAR(100) NULL,
  Gender         VARCHAR(20)  NULL,           -- мужской/женский
  Email          VARCHAR(255) NULL,
  BirthDate      DATE         NULL,
  CountryID      INTEGER      NULL,           -- FK на Country (по числовому коду)
  Phone          VARCHAR(30)  NULL,
  DirectionID    INTEGER      NULL,           -- FK на Direction
  Password       VARCHAR(50)  NULL,
  Photo          VARCHAR(100) NULL,
  FOREIGN KEY (CountryID)   REFERENCES Country(ID),
  FOREIGN KEY (DirectionID) REFERENCES Direction(ID)
);
INSERT INTO Jury VALUES(1,'Елисеев','Анатолий','Владленович','мужской','rsporer@stark.com','1962-04-18',NULL,'7(812)119-70-39',4,'qaayrn','foto14.jpg');
INSERT INTO Jury VALUES(2,'Кондратьев','Варлаам','Анатольевич','мужской','xlynch@brekke.org','1994-04-28',NULL,'7(370)956-48-86',1,'3P7zfU','foto15.jpg');
INSERT INTO Jury VALUES(3,'Копылов','Кирилл','Владимирович','мужской','bode.katelyn@hotmail.com','1998-01-30',NULL,'7(101)657-44-87',5,'71G82V','foto16.jpg');
INSERT INTO Jury VALUES(4,'Цветков','Иван','Семёнович','мужской','quigley.myron@bartell.com','1975-01-26',NULL,'7(098)883-75-75',5,'y1PKeW','foto17.jpg');
INSERT INTO Jury VALUES(5,'Суханов','Богдан','Денисович','мужской','megane97@gmail.com','1959-09-24',NULL,'7(051)994-61-67',2,'qy9gO8','foto18.jpg');
INSERT INTO Jury VALUES(6,'Кабанов','Роберт','Георгьевич','мужской','richie27@hotmail.com','1986-10-31',NULL,'7(335)776-48-63',4,'mi0NkX','foto19.jpg');
INSERT INTO Jury VALUES(7,'Тетерина','Жюли','Васильевна','женский','kaylah.watsica@cartwright.net','1989-03-16',NULL,'7(412)073-02-46',2,'q09Pcu','foto20.jpg');
INSERT INTO Jury VALUES(8,'Степанова','Эльмира','Васильевна','женский','fbrakus@yahoo.com','1998-10-19',NULL,'7(461)676-60-94',2,'agMR2O','foto21.jpg');
INSERT INTO Jury VALUES(9,'Потапова','Келен','Михайловна','женский','johnnie17@hotmail.com','1988-04-01',NULL,'7(706)652-88-45',2,'hLhjKT','foto22.jpg');
INSERT INTO Jury VALUES(10,'Николаев','Илларион','Антонинович','мужской','rasheed87@schuster.com','1966-11-17',NULL,'7(294)668-75-44',1,'90ZciI','foto23.jpg');
CREATE TABLE Moderator (
  ID             INTEGER PRIMARY KEY AUTOINCREMENT,
  LastName       VARCHAR(100) NOT NULL,
  FirstName      VARCHAR(100) NOT NULL,
  Patronymic     VARCHAR(100) NULL,
  Gender         VARCHAR(20)  NULL,
  Email          VARCHAR(255) NULL,
  BirthDate      DATE         NULL,
  CountryID      INTEGER      NULL,
  Phone          VARCHAR(30)  NULL,
  DirectionID    INTEGER      NULL,           -- направление модератора
  EventID        INTEGER      NULL,           -- мероприятие (по названию из xlsx)
  Password       VARCHAR(50)  NULL,
  Photo          VARCHAR(100) NULL,
  FOREIGN KEY (CountryID)   REFERENCES Country(ID),
  FOREIGN KEY (DirectionID) REFERENCES Direction(ID),
  FOREIGN KEY (EventID)     REFERENCES Event(ID)
);
INSERT INTO Moderator VALUES(1,'Селиванов','Тихон','Матвеевич','мужской','2qy9dgnot6cw@outlook.com','1996-07-04',NULL,'7(736)359-21-15',1,2,'222XXtSpa7','foto9.jpg');
INSERT INTO Moderator VALUES(2,'Иванов','Кирилл','Семёнович','мужской','ta5782yge4q9@outlook.com','1981-07-08',NULL,'7(780)027-80-28',1,2,'2xMj24vBT8','foto10.jpg');
INSERT INTO Moderator VALUES(3,'Петрова','Вероника','Андреевна','женский','tgiy2aqz0l63@mail.com','1965-11-02',NULL,'7(010)785-41-10',4,4,'6XUc2a98pY','foto8.jpg');
INSERT INTO Moderator VALUES(4,'Кузнецов','Фёдор','Макарович','мужской','dsi1b8a5vj9q@outlook.com','1991-08-24',NULL,'7(707)132-81-35',2,7,'6Avn58jTU5','foto11.jpg');
INSERT INTO Moderator VALUES(5,'Пантелеев','Руслан','Васильевич','мужской','wzepb50yj1c4@outlook.com','1964-06-29',NULL,'7(513)669-96-10',4,8,'d6jV6P7f8M','foto12.jpg');
INSERT INTO Moderator VALUES(6,'Гаврилов','Тимур','Робертович','мужской','wo7138p05bxf@mail.com','1984-08-14',NULL,'7(893)546-24-30',3,9,'3b3AYSf69r','foto13.jpg');
INSERT INTO Moderator VALUES(7,'Смирнов','Даниил','Михайлович','мужской','4o1thvw2fg97@gmail.com','1972-04-14',NULL,'7(734)601-23-18',1,12,'mf9PT8Y96m','foto14.jpg');
INSERT INTO Moderator VALUES(8,'Кулакова','Стефания','Ивановна','женский','wbkjoi56u0cx@gmail.com','1979-04-04',NULL,'7(052)308-74-92',5,15,'6sEpL6Yt24','foto16.jpg');
INSERT INTO Moderator VALUES(9,'Волков','Михаил','Дмитриевич','мужской','g2ureh9iacbq@mail.com','1983-04-27',NULL,'7(549)968-45-54',4,18,'Rk6s5pVU24','foto17.jpg');
INSERT INTO Moderator VALUES(10,'Степанов','Давид','Ильич','мужской','7ilhb2nkjda4@mail.com','1957-10-12',NULL,'7(786)943-23-62',3,19,'s3kVT3Zs68','foto18.jpg');
INSERT INTO Moderator VALUES(11,'Михайлов','Али','Кириллович','мужской','ew2csziqtvp5@mail.com','1993-05-23',NULL,'7(372)656-09-65',3,14,'3ZD5Cs2y5v','foto19.jpg');
INSERT INTO Moderator VALUES(12,'Наумов','Алексей','Викторович','мужской','im6pa0gvscyq@mail.com','1997-12-08',NULL,'7(238)857-64-34',5,19,'e9rJ429jLP','foto20.jpg');
INSERT INTO Moderator VALUES(13,'Рожкова','Алиса','Артёмовна','женский','xvhi3s0jza1p@tutanota.com','1991-03-05',NULL,'7(776)493-76-33',2,19,'cTd4p87T6B','foto21.jpg');
INSERT INTO Moderator VALUES(14,'Андреева','Злата','Фёдоровна','женский','lqhgwy8ema2n@tutanota.com','1982-10-31',NULL,'7(014)600-94-48',2,9,'3BcnR39Nd8','foto22.jpg');
INSERT INTO Moderator VALUES(15,'Яковлева','Анна','Дамировна','женский','xzrstfakhnj3@tutanota.com','1964-10-04',NULL,'7(231)843-32-09',2,9,'9yeX7U27Ka','foto23.jpg');
INSERT INTO Moderator VALUES(16,'Спиридонова','Василиса','Максимовна','женский','0r13bh2a4lxy@mail.com','1969-07-17',NULL,'7(496)606-80-00',5,12,'SCz3Ra4f37','foto24.jpg');
INSERT INTO Moderator VALUES(17,'Сергеева','Полина','Дмитриевна','женский','ga8liqyfp369@yahoo.com','1986-01-31',NULL,'7(065)497-80-67',5,14,'ryNBG568v9','foto25.jpg');
INSERT INTO Moderator VALUES(18,'Соловьев','Данила','Артёмович','мужской','b1ezkis4pqxw@outlook.com','1959-09-07',NULL,'7(907)004-97-65',4,14,'CU8Cp83k4h','foto26.jpg');
INSERT INTO Moderator VALUES(19,'Павлов','Константин','Ильич','мужской','c8svxqta2rhf@yahoo.com','1981-09-14',NULL,'7(243)545-29-16',3,14,'357Pk5hsGZ','foto27.jpg');
INSERT INTO Moderator VALUES(20,'Болдырева','Анна','Андреевна','женский','ycne3ilaxpoj@mail.com','1962-01-23',NULL,'7(956)552-26-23',5,15,'z6Bm3F4u9G','foto28.jpg');
INSERT INTO Moderator VALUES(21,'Волкова','Анна','Егоровна','женский','2wp8khydmre4@gmail.com','1951-03-26',NULL,'7(21)790-27-36',4,15,'68BgXGuy84','foto29.jpg');
CREATE TABLE Organizer (
  ID             INTEGER PRIMARY KEY AUTOINCREMENT,
  LastName       VARCHAR(100) NOT NULL,
  FirstName      VARCHAR(100) NOT NULL,
  Patronymic     VARCHAR(100) NULL,
  Gender         VARCHAR(20)  NULL,
  Email          VARCHAR(255) NULL,
  BirthDate      DATE         NULL,
  CountryID      INTEGER      NULL,
  Phone          VARCHAR(30)  NULL,
  Password       VARCHAR(50)  NULL,
  Photo          VARCHAR(100) NULL,
  FOREIGN KEY (CountryID) REFERENCES Country(ID)
);
INSERT INTO Organizer VALUES(1,'Богданов','Кирилл','Константинович','мужской','1g5u3fyiesdw@tutanota.com','1993-11-10',NULL,'7(712)665-36-07','3dzFF7z4S4','foto1.jpg');
INSERT INTO Organizer VALUES(2,'Ковалева','Анастасия','Олеговна','женский','fcdyuohxpza0@gmail.com','1992-12-29',NULL,'7(295)637-27-20','5YfY6ay6F6','foto2.jpg');
INSERT INTO Organizer VALUES(3,'Зимина','Ксения','Глебовна','женский','hiyrketgocn8@yahoo.com','1998-07-19',NULL,'7(520)444-26-69','3PxH55fc5V','foto3.jpg');
INSERT INTO Organizer VALUES(4,'Ковалева','Анастасия','Данииловна','женский','sf7z0c19egip@outlook.com','1986-01-14',NULL,'7(229)035-09-86','GV9m78mFf9','foto4.jpg');
INSERT INTO Organizer VALUES(5,'Чернышева','Мария','Георгиевна','женский','z5le0f3r2twy@gmail.com','1993-11-24',NULL,'7(568)897-31-04','J2mSrU65h9','foto5.jpg');
INSERT INTO Organizer VALUES(6,'Панов','Константин','Глебович','мужской','agjemv4725fp@tutanota.com','1999-07-26',NULL,'7(580)567-99-08','8UJR9mx2x3','foto6.jpg');
INSERT INTO Organizer VALUES(7,'Грачев','Данил','Дмитриевич','мужской','cx8fzvi2mes1@tutanota.com','1988-06-15',NULL,'7(151)116-73-26','8C22fx7JiF','foto7.jpg');
INSERT INTO Organizer VALUES(8,'Гордеева','София','Ивановна','женский','wxo8h5q1y2d9@outlook.com','1981-01-11',NULL,'7(056)380-73-66','Gn6Ae84Gu7','foto8.jpg');
INSERT INTO Organizer VALUES(9,'Золотарев','Егор','Фёдорович','мужской','m7a5xijdry1w@outlook.com','1987-09-02',NULL,'7(420)103-02-42','D9y6c25KYh','foto9.jpg');
INSERT INTO Organizer VALUES(10,'Столярова','Кристина','Давидовна','женский','6cqk8ug49drl@yahoo.com','1994-06-12',NULL,'7(553)369-09-97','jKx2eU3S89','foto10.jpg');
CREATE TABLE Member (
  ID             INTEGER PRIMARY KEY AUTOINCREMENT,
  LastName       VARCHAR(100) NOT NULL,
  FirstName      VARCHAR(100) NOT NULL,
  Patronymic     VARCHAR(100) NULL,
  Gender         VARCHAR(20)  NULL,
  Email          VARCHAR(255) NULL,
  BirthDate      DATE         NULL,
  CountryID      INTEGER      NULL,
  Phone          VARCHAR(30)  NULL,
  Password       VARCHAR(50)  NULL,
  Photo          VARCHAR(100) NULL,
  FOREIGN KEY (CountryID) REFERENCES Country(ID)
);
INSERT INTO Member VALUES(1,'Зиновьев','Лаврентий','Алексеевич','мужской','iqajcrysv921@tutanota.com','1974-09-27',NULL,'7(881)215-02-97','WpyIyK','foto60.jpg');
INSERT INTO Member VALUES(2,'Мишин','Исак','Максимович','мужской','sgujxkr3y815@mail.com','1982-04-14',NULL,'7(881)639-32-78','R0F5RQ','foto61.jpg');
INSERT INTO Member VALUES(3,'Воронцов','Илларион','Пантелеймонович','мужской','91i5yv46efl7@tutanota.com','1998-06-17',NULL,'7(881)950-40-96','wFuOu2','foto62.jpg');
INSERT INTO Member VALUES(4,'Тарасов','Ким','Федотович','мужской','2id46h8elpzx@outlook.com','1980-10-01',NULL,'7(881)132-48-34','B9A9G0','foto3.jpg');
INSERT INTO Member VALUES(5,'Казаков','Станислав','Лукьянович','мужской','j80e1zy79p3v@mail.com','1975-07-25',NULL,'7(881)501-79-85','2p5dKr','foto4.jpg');
INSERT INTO Member VALUES(6,'Васильев','Абрам','Феликсович','мужской','gia5l3ytuw2c@gmail.com','1984-12-26',NULL,'7(881)149-41-85','BzT3im','foto5.jpg');
INSERT INTO Member VALUES(7,'Ильин','Бенедикт','Адольфович','мужской','km6saojbwzn9@yahoo.com','1977-03-30',NULL,'7(881)466-56-23','E0m5Um','foto6.jpg');
INSERT INTO Member VALUES(8,'Киселёв','Василий','Евсеевич','мужской','cv28dw5b1om9@mail.com','1979-10-22',NULL,'7(881)551-49-65','s1NYWs','foto7.jpg');
INSERT INTO Member VALUES(9,'Панов','Виталий','Федосеевич','мужской','mc7q6n0eox5p@tutanota.com','1985-06-09',NULL,'7(881)662-54-71','brHpQS','foto8.jpg');
INSERT INTO Member VALUES(10,'Якушев','Богдан','Ефимович','мужской','k6eyq18bpon4@tutanota.com','1984-04-11',NULL,'7(881)211-40-75','JJigbW','foto9.jpg');
INSERT INTO Member VALUES(11,'Самойлов','Гордей','Семёнович','мужской','bgvajqde65yh@mail.com','1993-02-14',NULL,'7(881)329-94-36','Q7Ko7E','foto10.jpg');
INSERT INTO Member VALUES(12,'Михайлов','Абрам','Демьянович','мужской','ekudbzqf4jcm@gmail.com','1988-01-15',NULL,'7(881)984-84-03','BKcWXr','foto11.jpg');
INSERT INTO Member VALUES(13,'Воробьёв','Никифор','Евсеевич','мужской','uywi321694rt@tutanota.com','1980-11-30',NULL,'7(881)656-13-78','CvjQ1n','foto12.jpg');
INSERT INTO Member VALUES(14,'Тихонов','Ермак','Донатович','мужской','ompve5atd4lr@tutanota.com','1971-04-01',NULL,'7(881)990-96-64','myFi1v','foto13.jpg');
CREATE TABLE Activity (
  ID           INTEGER PRIMARY KEY AUTOINCREMENT,
  EventID      INTEGER      NOT NULL,          -- FK на Event
  Title        VARCHAR(300) NOT NULL,          -- Наименование активности
  Day          INTEGER      NULL,              -- День
  StartTime    VARCHAR(10)  NULL,              -- Время начала (HH:MM)
  ModeratorID  INTEGER      NULL,              -- FK на Moderator
  Jury1ID      INTEGER      NULL,              -- FK на Jury
  Jury2ID      INTEGER      NULL,
  Jury3ID      INTEGER      NULL,
  Jury4ID      INTEGER      NULL,
  Jury5ID      INTEGER      NULL,
  WinnerID     INTEGER      NULL,              -- FK на Member (победитель)
  FOREIGN KEY (EventID)     REFERENCES Event(ID),
  FOREIGN KEY (ModeratorID) REFERENCES Moderator(ID),
  FOREIGN KEY (Jury1ID)     REFERENCES Jury(ID),
  FOREIGN KEY (Jury2ID)     REFERENCES Jury(ID),
  FOREIGN KEY (Jury3ID)     REFERENCES Jury(ID),
  FOREIGN KEY (Jury4ID)     REFERENCES Jury(ID),
  FOREIGN KEY (Jury5ID)     REFERENCES Jury(ID),
  FOREIGN KEY (WinnerID)    REFERENCES Member(ID)
);
CREATE TABLE IF NOT EXISTS "Order" (
  ID           INTEGER PRIMARY KEY AUTOINCREMENT,
  MemberID     INTEGER NOT NULL,          -- кто покупает (FK на Member)
  EventID      INTEGER NOT NULL,          -- на какое мероприятие (FK на Event)
  Quantity     INTEGER NOT NULL,          -- сколько билетов
  TotalPrice   NUMERIC NOT NULL,          -- итоговая сумма
  OrderDate    DATETIME NOT NULL,         -- когда оформлен
  Status       VARCHAR(20) NOT NULL DEFAULT 'new', Article VARCHAR(50) DEFAULT 'ORD-101', DeliveryDate DATE DEFAULT '2026-04-10', PickupPointID INTEGER DEFAULT 1 REFERENCES PickupPoint(ID), ProductID INTEGER REFERENCES Product(ID),
  FOREIGN KEY (MemberID) REFERENCES Member(ID),
  FOREIGN KEY (EventID)  REFERENCES Event(ID)
);
CREATE TABLE IF NOT EXISTS "TicketPrice" (
  DirectionID INTEGER PRIMARY KEY,
  Price       NUMERIC NOT NULL,
  FOREIGN KEY (DirectionID) REFERENCES Direction(ID)
);
INSERT INTO TicketPrice VALUES(1,1500);
INSERT INTO TicketPrice VALUES(2,1200);
INSERT INTO TicketPrice VALUES(3,1000);
INSERT INTO TicketPrice VALUES(4,2000);
INSERT INTO TicketPrice VALUES(5,2500);
CREATE TABLE PickupPoint (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            Address TEXT NOT NULL
        );
INSERT INTO PickupPoint VALUES(1,'г. Москва, ул. Ленина, д. 15');
INSERT INTO PickupPoint VALUES(2,'г. Санкт-Петербург, пр. Мира, д. 40');
INSERT INTO PickupPoint VALUES(3,'г. Казань, ул. Баумана, д. 7');
INSERT INTO sqlite_sequence VALUES('Direction',5);
INSERT INTO sqlite_sequence VALUES('Event',20);
INSERT INTO sqlite_sequence VALUES('Jury',10);
INSERT INTO sqlite_sequence VALUES('Moderator',21);
INSERT INTO sqlite_sequence VALUES('Organizer',10);
INSERT INTO sqlite_sequence VALUES('Member',14);
INSERT INTO sqlite_sequence VALUES('PickupPoint',3);
INSERT INTO sqlite_sequence VALUES('ProductType',2);
INSERT INTO sqlite_sequence VALUES('Supplier',1);
INSERT INTO sqlite_sequence VALUES('Product',1);
CREATE INDEX idx_agent_title       ON Agent(Title);
CREATE INDEX idx_agent_type        ON Agent(AgentTypeID);
CREATE INDEX idx_productsale_agent ON ProductSale(AgentID);
CREATE INDEX idx_productsale_date  ON ProductSale(SaleDate);
CREATE INDEX idx_event_city          ON Event(CityID);
CREATE INDEX idx_event_direction     ON Event(DirectionID);
CREATE INDEX idx_activity_event      ON Activity(EventID);
CREATE INDEX idx_activity_moderator  ON Activity(ModeratorID);
CREATE INDEX idx_jury_country        ON Jury(CountryID);
CREATE INDEX idx_member_country      ON Member(CountryID);
CREATE INDEX idx_moderator_event     ON Moderator(EventID);
COMMIT;
