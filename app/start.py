from flask import Flask
from flask import request
from flask import render_template
from flask import g

import sqlite3


DATABASE = '../db/database.db'

app = Flask(__name__)
app.app_context().push()

# class Logins(db.Model):
#     id = db.Column('login_id', db.Integer, primary_key = True)
#     username = db.Column(db.String(32))
#     password = db.Column(db.String(32))
    
#     def __init__(self, username, password):
#         self.username = username
#         self.password = password

# class Cars(db.Model):
#     id = db.Column('id', db.Integer, primary_key = True)
#     name = db.Column(db.String(100))
#     color = db.Column(db.String(32))
#     price = db.Column(db.Float())
    
#     def __init__(self, name, color, price):
#         self.name = name
#         self.color = color
#         self.price = price

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
        return "Empty"

    # logins = Logins.query.all()
    # for l in range(len(logins)):
    #     if logins[l].username == usrname and logins[l].password == psswd:
    #         return "Ok"
    
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

