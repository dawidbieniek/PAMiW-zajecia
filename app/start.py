from flask import Flask
from flask import request
from flask import render_template
from flask import g

import sqlite3

DATABASE = '../db/database.db'

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login.html")
def loginPage():
    return render_template("login.html")

@app.route("/login.html", methods=["POST"])
def loginPageLogIn():
    usrname = request.get_json().get("username")
    psswd = request.get_json().get("password")
    
    if(usrname == "" or psswd == ""):
        return "Podaj login i hasło"

    logins = Logins.query.all()
    for l in range(len(logins)):
        if logins[l].username == usrname and logins[l].password == psswd:
            return "Ok"
    
    return "Invalid"


@app.route("/search.html")
def searchPage():
    return render_template("search.html")


@app.route("/search.html", methods=["POST"])
def searchPageSearch():
    name = request.get_json().get("name")
    
    # if(name == ""):
    #     cars = Cars.query.all()
    # else:
    #     cars = Cars.query.filter(Cars.name.contains(name)).all()
    # return jsonify({'response': render_template('carTable.html', cars=cars)})
    return jsonify({'response' : "Nie dostępne"})

    
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

