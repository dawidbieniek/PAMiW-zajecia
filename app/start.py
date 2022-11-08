from flask import Flask, request, render_template, url_for, redirect

from contextlib import closing

from bcrypt import checkpw, gensalt, hashpw

import sqlite3

import sys

DB_PATH = "../db/database.db"
app = Flask(__name__)

@app.route("/")
def indexPage():
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def loginPage():
    # POST
    if request.method == "POST":
        usrname = request.get_json().get("username")
        psswd = request.get_json().get("password")

        if(usrname == "" or psswd == ""):
            return "Podaj login i hasło", 200
        
        encodedPsswd = psswd.encode("utf-8")
        dbHash = query(f"SELECT usrname, passwd FROM users WHERE usrname = '{usrname}'")[0][1].encode("utf-8")
        if(checkpw(encodedPsswd, dbHash)):
            return "OK", 200
            
        return "Niepoprawne dane logowania", 200
    # GET
    return render_template("login.html")
    

@app.route("/login/register", methods = ["GET", "PUT"])
def registerPage():
    # PUT
    if request.method == "PUT":
        usrname = request.get_json().get("username")
        psswd = request.get_json().get("password")
        reppsswd = request.get_json().get("repPassword")

        if(usrname == "" or psswd == "" or reppsswd == ""):
            return "Podaj wszystkie dane", 200
        # Check if passwords match
        if(psswd != reppsswd):
            return "Hasła muszą być identyczne", 200
        # Check if login already exists
        
        if(len(query(f"SELECT usrname FROM users WHERE usrname = '{usrname}'")) > 0):
            return "Login już jest zajęty", 200
        # Register user
        hashed = hashpw(psswd.encode("utf-8"), gensalt())
        query(f"INSERT INTO users (usrname, passwd) VALUES ('{usrname}', '{hashed.decode('utf-8')}')")
        # return redirect(url_for(loginPage), 201)
        return "", 204

    # GET
    return render_template("register.html")
    

@app.route("/carSearch", methods = ["GET", "POST"])
def carSearchPage():
    # POST
    if request.method == "POST":
        text = request.get_json().get("query")
        if(not text or text == ""):
            cars = query(f"SELECT * FROM cars")
        else:
            cars = query(f"SELECT * FROM cars WHERE carName LIKE '%{text}%'")
        return render_template('tables/carTable.html', cars=cars), 200
    
    # GET
    return render_template("carSearch.html")

@app.route("/userList", methods = ["GET"])
def userListPage():
    users = query("SELECT usrname, passwd FROM users")
    return render_template("userList.html", users=users)


def query(sql):
    with closing(sqlite3.connect(DB_PATH)) as con, con, closing(con.cursor()) as cur:
        cur.execute(sql)
        return cur.fetchall()


def log(msg):
    print(msg, file=sys.stderr)