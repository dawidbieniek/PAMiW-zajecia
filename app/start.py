from flask import Flask
from flask import request
from flask import render_template

from contextlib import closing

import sqlite3

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
            return "Podaj login i hasło"

        data = query("SELECT usrname, passwd FROM users")
        for r in data:
            if(r[0] == usrname and r[1] == psswd):
                return "OK"
            
        return "Niepoprawne dane logowania"
    # GET
    return render_template("login.html")
    

@app.route("/login/register", methods = ["GET", "POST"])
def registerPage():
    # POST
    if request.method == "POST":
        usrname = request.get_json().get("username")
        psswd = request.get_json().get("password")
        reppsswd = request.get_json().get("repPassword")

        if(usrname == "" or psswd == "" or reppsswd == ""):
            return "Podaj wszystkie dane"
        if(psswd != reppsswd):
            return "Hasła muszą być identyczne"

    # GET
    return render_template("register.html")
    

@app.route("/search", methods = ["GET", "POST"])
def searchPage():
    # POST
    if request.method == "POST":
        name = request.get_json().get("name")
        
        # if(name == ""):
        #     cars = Cars.query.all()
        # else:
        #     cars = Cars.query.filter(Cars.name.contains(name)).all()
        # return jsonify({'response': render_template('carTable.html', cars=cars)})
        return jsonify({"response" : "Nie dostępne"})
    
    # GET
    return render_template("search.html")

@app.route("/userList", methods = ["GET"])
def userListPage():
    users = query("SELECT id, usrname AS login, passwd AS password FROM users")
    return render_template("userList.html", users=users)


def query(sql):
    with closing(sqlite3.connect(DB_PATH)) as con, con,  \
            closing(con.cursor()) as cur:
        cur.execute(sql)
        return cur.fetchall()
