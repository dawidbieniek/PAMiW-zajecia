DROP TABLE IF EXISTS email;
DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS car;

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
    content TEXT,
    FOREIGN KEY(toUsername) REFERENCES user(username),
    FOREIGN KEY(fromUsername) REFERENCES user(username)
);