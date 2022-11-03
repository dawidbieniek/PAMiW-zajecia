import sqlite3

def testTable(tableName):
    data = db.execute(f"PRAGMA table_info({tableName})").fetchall()
    print(f"{tableName}:")
    for r in data:
        print("\t", r)

if __name__ == "__main__":
    db = sqlite3.connect("database.db")

    with open("schema.sql") as f:
        db.executescript(f.read())

    print("Created tables:")
    tables = db.execute("SELECT name FROM sqlite_master WHERE type ='table' AND name NOT LIKE 'sqlite_%'").fetchall()
    for t in tables:
        testTable(t[0])

    db.close()
