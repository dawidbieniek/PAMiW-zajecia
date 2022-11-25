import sqlite3

def printTable(tableName):
    data = db.execute(f"SELECT * FROM {tableName}").fetchall()
    print(f"{tableName}:")
    for r in data:
        print("\t", r)

if __name__ == "__main__":
    db = sqlite3.connect("db/database.db")

    with open("db/testData.sql") as f:
        if(len(db.execute("SELECT * FROM user").fetchall()) > 0):
            print("Database is already populated")
            db.close()
            exit()

        db.executescript(f.read())

    print("Tables content:")
    printTable("user")
    printTable("car")
    printTable("email")

    db.close()
