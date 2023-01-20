import sqlite3

def testTable(tableName, database):
    data = database.execute(f"PRAGMA table_info({tableName})").fetchall()
    print(f"{tableName}:")
    for r in data:
        print("\t", r)

if __name__ == "__main__":
    db = sqlite3.connect("database.db")
    dbRes = sqlite3.connect("databaseRes.db")

    with open("schema.sql") as f:
        db.executescript(f.read())
    with open("schemaRes.sql") as f:
        dbRes.executescript(f.read())

    print("Created tables:")
    tables = db.execute("SELECT name FROM sqlite_master WHERE type ='table' AND name NOT LIKE 'sqlite_%'").fetchall()
    for t in tables:
        testTable(t[0], db)
        
    tables = dbRes.execute("SELECT name FROM sqlite_master WHERE type ='table' AND name NOT LIKE 'sqlite_%'").fetchall()
    for t in tables:
        testTable(t[0], dbRes)

    db.close()
    dbRes.close()
