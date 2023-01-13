DROP TABLE IF EXISTS email;
DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS car;
DROP TABLE IF EXISTS reservation;

CREATE TABLE user
(
    username TEXT(32) PRIMARY KEY,
    password TEXT(128) NOT NULL,
    isadmin INTEGER
);

CREATE TABLE car
(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    carName TEXT(32),
    color TEXT(32),
    price REAL
);

CREATE TABLE email
(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    toUsername TEXT(32),
    fromUsername TEXT(32),
    topic TEXT(256),
    content TEXT,
    FOREIGN KEY(toUsername) REFERENCES user(username),
    FOREIGN KEY(fromUsername) REFERENCES user(username)
);

CREATE TABLE reservation
(
    id TEXT(32) PRIMARY KEY NOT NULL,
    startDate DATE NOT NULL,
    userId INTEGER NOT NULL,
    carId INTEGER NOT NULL,
    FOREIGN KEY(userId) REFERENCES user(username),
    FOREIGN KEY(carId) REFERENCES car(id)
);