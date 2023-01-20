DROP TABLE IF EXISTS reservation;

CREATE TABLE reservation
(
    id TEXT(32) PRIMARY KEY NOT NULL,
    startDate DATE NOT NULL,
    userId INTEGER NOT NULL,
    carId INTEGER NOT NULL,
    FOREIGN KEY(userId) REFERENCES user(username),
    FOREIGN KEY(carId) REFERENCES car(id)
);