import sqlite3

def printTable(tableName, database):
    data = database.execute(f"SELECT * FROM {tableName}").fetchall()
    print(f"{tableName}:")
    for r in data:
        print("\t", r)

if __name__ == "__main__":
    db = sqlite3.connect("database.db")
    dbRes = sqlite3.connect("databaseRes.db")

    with open("testData.sql") as f:
        if(len(db.execute("SELECT * FROM user").fetchall()) > 0):
            print("Database is already populated")
            db.close()
            dbRes.close()
            exit()

        db.executescript(f.read())

    print("Tables content:")
    printTable("user", db)
    printTable("car", db)
    printTable("message", db)
    printTable("blackTokens", db)
    printTable("reservation", dbRes)

    db.close()
    dbRes.close()
