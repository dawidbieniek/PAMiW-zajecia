from flask import Flask, request, render_template, url_for, redirect, session, abort
from bcrypt import checkpw, gensalt, hashpw
from contextlib import closing
from functools import wraps
import secrets
import sqlite3
import sys

from User import User

DB_PATH = "../db/database.db"

app = Flask(__name__)

app.jinja_env.line_statement_prefix = "#"

app.config["SESSION_PERMANENT"] = False
app.config["SECRET_KEY"] = secrets.token_urlsafe(16)

def requireLogin(func):
    @wraps(func)
    def secure_function(*args, **kwargs):
        if not isLoggedin():
            log("Redirect")
            return redirect(url_for("loginPage", next=request.url))
        return func(*args, **kwargs)
    return secure_function


@app.route("/")
def indexPage():
    return render_template("index.html", user=session.get("login", None))


@app.route("/logout")
def logout():
    if(session.get("login", None) != None):
        # session.pop("login", None)
        session.clear()
    return redirect(url_for("indexPage"))

@app.route("/login", methods=["GET", "POST"])
def loginPage():
    if isLoggedin():
        return redirect(url_for("indexPage"))
    # POST
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        nextUrl = request.form.get("next")

        if username == "" or password == "":
            return render_template(
                "login.html",
                msg="Podaj login i hasło",
                username=(username if username else None),
            )

        userData = querySingle(f"SELECT * FROM user WHERE username = '{username}'")
        if userData and checkPassword(username, password):
            session["login"] = User(userData[0], userData[2]).__dict__
            log(nextUrl)
            if(nextUrl):
                return redirect(nextUrl)
            return redirect(url_for("indexPage"))

        return render_template(
            "login.html", msg="Niepoprawne dane logowania", username=username
        )
    # GET
    log(request.args)
    return render_template("login.html", next=request.args.get("next", ""))


@app.route("/login/register", methods=["GET", "POST"])
def registerPage():
    if isLoggedin():
        return redirect(url_for("indexPage"))
    # POST
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        repPassword = request.form.get("repPassword")

        if username == "" or password == "" or repPassword == "":
            return render_template(
                "register.html",
                msg="Podaj wszystkie dane",
                username=(username if username else None),
            )
        # Check if passwords match
        if password != repPassword:
            return render_template(
                "register.html", msg="Hasła muszą być identyczne", username=username
            )
        # Check if login already exists
        if len(query(f"SELECT username FROM user WHERE username = '{username}'")) > 0:
            return render_template(
                "register.html", msg="Login już jest zajęty", username=username
            )
        # Register user
        hashed = hashpw(password.encode("utf-8"), gensalt())
        query(
            f"INSERT INTO user VALUES ('{username}', '{hashed.decode('utf-8')}', FALSE)"
        )
        return redirect(url_for("loginPage"))

    # GET
    return render_template("register.html")

@app.route("/login/changePassword", methods=["GET", "POST"])
@requireLogin
def changePasswordPage():

    # POST
    if request.method == "POST":
        password = request.form.get("password")
        newPassword = request.form.get("newPassword")
        repNewPassword = request.form.get("repNewPassword")

        if password == "" or newPassword == "" or repNewPassword == "":
            return render_template("changePassword.html", msg="Podaj wszystkie dane")
        # Check if passwords match
        if newPassword != repNewPassword:
            return render_template(
                "changePassword.html", msg="Nowe hasła muszą być identyczne"
            )
        # Check if new password is new
        if newPassword == password:
            return render_template(
                "changePassword.html", msg="Nowe hasło musi różnić się od starego"
            )
        # Check if old password is correct
        username = session["login"]["username"]
        if not checkPassword(username, password):
            return render_template("changePassword.html", msg="Niepoprawne hasło")
        # Update password
        hashed = hashpw(newPassword.encode("utf-8"), gensalt())
        query(
            f"UPDATE user SET password = '{hashed.decode('utf-8')}' WHERE username = '{username}'"
        )
        return redirect(url_for("loginPage"))
    # GET
    return render_template("changePassword.html")


@app.route("/account", methods=["GET"])
@requireLogin
def accountPage():

    user = session.get("login", None)
    if user:
        return render_template("account.html", user=user)
    return redirect(url_for("loginPage"))


@app.route("/account/messages")
@requireLogin
def emailPage():

    return render_template("emails.html")

@app.route("/account/messages/newMessage", methods=["GET", "POST"])
@requireLogin
def newEmailPage():

    if request.method == "POST":
        fromUsername = session["login"]["username"]
        toUsername = request.form.get("to")
        topis = request.form.get("topic")
        content = request.form.get("content")

        if (
            len(query(f"SELECT username FROM user WHERE username = '{toUsername}'"))
            == 0
        ):
            return render_template("newEmail.html", msg="Podany adresat nie istnieje", toUsername=toUsername, content=content)
        query(
            f"INSERT INTO email (toUsername, fromUsername, topic content) VALUES ('{toUsername}', '{fromUsername}', '{topic}', '{content}')"
        )
        return redirect(url_for("emailPage"))

    return render_template("newEmail.html")


@app.route("/carSearch", methods=["GET", "POST"])
def carSearchPage():
    # POST
    if request.method == "POST":
        text = request.get_json().get("query")
        if not text or text == "":
            cars = query(f"SELECT * FROM car")
        else:
            cars = query(f"SELECT * FROM car WHERE carName LIKE '%{text}%'")
        return render_template("tables/carTable.html", cars=cars)

    # GET
    return render_template("carSearch.html")

@app.route("/userList", methods=["GET"])
def userListPage():
    if not isCurrentUserAdmin():
        return abort(403)
    users = query("SELECT * FROM user")
    return render_template("userList.html", users=users)


@app.route("/api/messageCount")
def apiMessageCount():
    if not isLoggedin():
        return 0
    numberOfMsgs = querySingle(
        f"SELECT COUNT(*) FROM email WHERE toUsername = '{session['login']['username']}'"
    )[0]
    return str(numberOfMsgs)


@app.route("/api/isLoggedIn")
def apiLoggedIn():
    return str(isLoggedin())


def query(sql):
    with closing(sqlite3.connect(DB_PATH)) as con, con, closing(con.cursor()) as cur:
        cur.execute(sql)
        return cur.fetchall()


def querySingle(sql):
    with closing(sqlite3.connect(DB_PATH)) as con, con, closing(con.cursor()) as cur:
        cur.execute(sql)

        return cur.fetchone()


def checkPassword(username, password):
    userData = querySingle(f"SELECT * FROM user WHERE username = '{username}'")
    if not userData:
        return False
    encodedPassword = password.encode("utf-8")
    dbHash = userData[1].encode("utf-8")
    return checkpw(encodedPassword, dbHash)


def isLoggedin():
    return session.get("login", None) != None


def isCurrentUserAdmin():
    if not isLoggedin():
        return False

    return (
        querySingle(
            f"SELECT isadmin FROM user WHERE username = '{session['login']['username']}'"
        )
    )[0] == 1


def log(msg):
    print(msg, file=sys.stderr)
