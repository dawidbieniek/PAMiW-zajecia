from contextlib import closing
import sqlite3

DB_PATH = "../db/database.db"

def query(sql):
    with closing(sqlite3.connect(DB_PATH)) as con, con, closing(con.cursor()) as cur:
        cur.execute(sql)
        return cur.fetchall()

def querySingle(sql):
    with closing(sqlite3.connect(DB_PATH)) as con, con, closing(con.cursor()) as cur:
        cur.execute(sql)
        return cur.fetchone()
