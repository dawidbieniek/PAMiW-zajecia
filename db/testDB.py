import sqlite3

db = sqlite3.connect("database.db")

if __name__ == "__main__":
    data = db.execute("SELECT * FROM users").fetchall()
    for r in data:
        print(r[0], r[1], r[2])
    data = db.execute("SELECT * FROM cars").fetchall()
    for r in data:
        print(r[0], r[1], r[2], r[3])
