DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS cars;

CREATE TABLE users
(
    username TEXT(32) PRIMARY KEY,
    password TEXT(128) NOT NULL,
    isadmin INTEGER
);

CREATE TABLE cars
(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    carName TEXT(32),
    color TEXT(32),
    price REAL
);