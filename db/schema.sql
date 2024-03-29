DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS car;
DROP TABLE IF EXISTS message;
DROP TABLE IF EXISTS blackTokens;

CREATE TABLE user
(
    username TEXT(32) PRIMARY KEY,
    email TEXT(64),
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

CREATE TABLE message
(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    toUsername TEXT(32),
    fromUsername TEXT(32),
    topic TEXT(256),
    content TEXT,
    FOREIGN KEY(toUsername) REFERENCES user(username),
    FOREIGN KEY(fromUsername) REFERENCES user(username)
);

CREATE TABLE blackTokens
(
    token TEXT PRIMARY KEY NOT NULL,
    deleteDate DATE NOT NULL
);