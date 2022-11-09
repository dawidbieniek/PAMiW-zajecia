from flask import Flask, request, render_template, url_for, redirect, session, abort
from bcrypt import checkpw, gensalt, hashpw
# from flask_login import LoginManager
from contextlib import closing
import secrets

import sqlite3

import sys

from User import User

DB_PATH = "../db/database.db"

app = Flask(__name__)

app.config["SECRET_KEY"] = secrets.token_urlsafe(16)

# loginManager = LoginManager()
# loginManager.init_app(app)

@app.route("/")
def indexPage():
    return render_template("index.html", user=session.get("login", None))

@app.route("/logout")
def logout():
    session.pop("login", None)
    return redirect(url_for("indexPage"))

@app.route("/login", methods=["GET", "POST"])
def loginPage():
    if(isLoggedin()):
        return redirect(url_for("indexPage"))
    # POST
    if request.method == "POST":
        username = request.get_json().get("username")
        password = request.get_json().get("password")

        if(username == "" or password == ""):
            return "Podaj login i hasło", 200
        
        userData = querySingle(f"SELECT * FROM users WHERE username = '{username}'")
        if(userData and checkPassword(username, password)):
            session["login"] = User(userData[0], userData[2]).__dict__
            return "OK", 200
            
        return "Niepoprawne dane logowania", 200
    # GET
    return render_template("login.html")

@app.route("/login/register", methods = ["GET", "PUT"])
def registerPage():
    if(isLoggedin()):
        return redirect(url_for("indexPage"))
    # PUT
    if request.method == "PUT":
        username = request.get_json().get("username")
        password = request.get_json().get("password")
        repPassword = request.get_json().get("repPassword")

        if(username == "" or password == "" or repPassword == ""):
            return "Podaj wszystkie dane", 200
        # Check if passwords match
        if(password != repPassword):
            return "Hasła muszą być identyczne", 200
        # Check if login already exists        
        if(len(query(f"SELECT username FROM users WHERE username = '{username}'")) > 0):
            return "Login już jest zajęty", 200
        # Register user
        hashed = hashpw(password.encode("utf-8"), gensalt())
        query(f"INSERT INTO users VALUES ('{username}', '{hashed.decode('utf-8')}', FALSE)")
        # return redirect(url_for("loginPage"), 201)
        return "Dodano użytkownika", 200

    # GET
    return render_template("register.html")

@app.route("/login/changePassword", methods =["GET", "UPDATE"])
def changePasswordPage():
    if(not isLoggedin()):
        return abort(403)
    # UPDATE
    if(request.method == "UPDATE"):
        password = request.get_json().get("password")
        newPassword = request.get_json().get("newPassword")
        repNewPassword = request.get_json().get("repNewPassword")

        if(password == "" or newPassword == "" or repNewPassword == ""):
            return "Podaj wszystkie dane", 200
        # Check if passwords match
        if(newPassword != repNewPassword):
            return "Nowe hasła muszą być identyczne", 200
        # Check if new password is new
        if(newPassword == password):
            return "Nowe hasło musi różnić się od starego", 200
        # Check if old password is correct
        username = session["login"]["username"]
        if(not checkPassword(username, password)):
            return "Niepoprawne hasło", 200
        # Update password
        hashed = hashpw(newPassword.encode("utf-8"), gensalt())
        query(f"UPDATE users SET password = '{hashed.decode('utf-8')}' WHERE username = '{username}'")
        # return redirect(url_for("loginPage"), 201)
        return "Zmieniono hasło", 200
    # GET
    return render_template("changePassword.html", user = session["login"])

@app.route("/account", methods =["GET"])
def accountPage():
    user = session.get("login", None)
    if(user):
        return render_template("account.html", user = user)
    return redirect(url_for("loginPage"))

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
    if(not isCurrentUserAdmin()):
        return abort(403)
    users = query("SELECT * FROM users")
    return render_template("userList.html", users=users)


def query(sql):
    with closing(sqlite3.connect(DB_PATH)) as con, con, closing(con.cursor()) as cur:
        cur.execute(sql)
        return cur.fetchall()

def querySingle(sql):
    with closing(sqlite3.connect(DB_PATH)) as con, con, closing(con.cursor()) as cur:
        cur.execute(sql)

        return cur.fetchone()

def checkPassword(username, password):
    userData = querySingle(f"SELECT * FROM users WHERE username = '{username}'")
    if(not userData):
        return False
    encodedPassword = password.encode("utf-8")
    dbHash = userData[1].encode("utf-8")
    return checkpw(encodedPassword, dbHash)

def isLoggedin():
    return session.get("login", None) != None

def isCurrentUserAdmin():
    if(not isLoggedin()):
        return False

    return (querySingle(f"SELECT isadmin FROM users WHERE username = '{session['login']['username']}'"))[0] == 1

def log(msg):
    print(msg, file=sys.stderr)