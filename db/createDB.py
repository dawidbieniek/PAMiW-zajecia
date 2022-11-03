import sqlite3

DATABASE = sqlite3.connect("database.db")

with open("schema.sql") as f:
    DATABASE.executescript(f.read())