DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS cars;

CREATE TABLE users
(
    usrname TEXT(32) PRIMARY KEY,
    passwd TEXT(128)
);

CREATE TABLE cars
(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    carName TEXT(32),
    color TEXT(32),
    price REAL
);