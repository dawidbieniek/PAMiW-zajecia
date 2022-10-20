from flask import Flask
from flask import request
from flask import jsonify
# from flask import session
from flask import render_template

from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.app_context().push()
databaseName = "login.sqlite3"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + databaseName
app.config['SECRET_KEY'] = "random string"

db = SQLAlchemy(app)
class Logins(db.Model):
    id = db.Column('login_id', db.Integer, primary_key = True)
    username = db.Column(db.String(32))
    password = db.Column(db.String(32))
    
    def __init__(self, username, password):
        self.username = username
        self.password = password

class Cars(db.Model):
    id = db.Column('id', db.Integer, primary_key = True)
    name = db.Column(db.String(100))
    color = db.Column(db.String(32))
    price = db.Column(db.Float())
    
    def __init__(self, name, color, price):
        self.name = name
        self.color = color
        self.price = price

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
    
    if(name == ""):
        cars = Cars.query.all()
    else:
        cars = Cars.query.filter(Cars.name.contains(name)).all()
    return jsonify({'response': render_template('carTable.html', cars=cars)})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050)
