CREATE TABLE users
(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usrname TEXT(32),
    passwd TEXT(128)
);

CREATE TABLE cars
(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    carName TEXT(32),
    color TEXT(32),
    price REAL
);