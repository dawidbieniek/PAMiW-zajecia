from flask import Flask
from flask import request
from flask import render_template
from flask import g

import sqlite3

DATABASE = "../db/database.db"

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login")
def loginPage():
    return render_template("login.html")

@app.route("/login/authenticate", methods=["POST"])
def loginPageLogIn():
    usrname = request.get_json().get("username")
    psswd = request.get_json().get("password")
    
    if(usrname == "" or psswd == ""):
        return "Podaj login i hasło"

    data = getDb().execute("SELECT usrname, passwd FROM users").fetchall()
    for r in data:
        if(r[0] == usrname and r[1] == psswd):
            return "OK"
        
    return "Niepoprawne dane logowania"


@app.route("/search")
def searchPage():
    return render_template("search.html")


@app.route("/search", methods=["POST"])
def searchPageSearch():
    name = request.get_json().get("name")
    
    # if(name == ""):
    #     cars = Cars.query.all()
    # else:
    #     cars = Cars.query.filter(Cars.name.contains(name)).all()
    # return jsonify({'response': render_template('carTable.html', cars=cars)})
    return jsonify({"response" : "Nie dostępne"})

    
def getDb():
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE)
    return g.db

@app.teardown_appcontext
def closeConnection(exception):
    db = g.pop("db", None)

    if db is not None:
        db.close()

