from flask import Flask, request, render_template, url_for, redirect, session, abort
from bcrypt import checkpw, gensalt, hashpw
from contextlib import closing
from functools import wraps
from dotenv import load_dotenv
from os import getenv
from requests import Request, post, get
from string import ascii_letters, digits
from qrcode import QRCode
from flask_mail import Mail, Message
from datetime import datetime
from datetime import timedelta
import random
import secrets
import sqlite3
import sys
import json
import uuid
import base64
import io
import jwt

from User import User

load_dotenv(verbose=True)

DB_PATH = "../db/database.db"
GH_CLIENT_ID = getenv("CLIENT_ID")
GH_CLIENT_SECRET = getenv("CLIENT_SECRET")
GM_USERNAME = getenv("GM_USERNAME")
GM_PASSWORD = getenv("GM_PASSWORD")
JWT_KEY = getenv("JWT_KEY")

app = Flask(__name__)

app.jinja_env.line_statement_prefix = "#"

app.config["SESSION_PERMANENT"] = False
app.config["SECRET_KEY"] = secrets.token_urlsafe(16)
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = GM_USERNAME
app.config['MAIL_PASSWORD'] = GM_PASSWORD

mail = Mail(app)

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

@app.route("/logout", methods=["GET"])
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
    msg = request.args.get("msg", None)
    if msg != None:
        return render_template("login.html", msg=msg)
    else:
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
            f"INSERT INTO user VALUES ('{username}', '{hashed.decode('utf-8')}', 0, 'dawid_b01@wp.pl')"
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

@app.route("/login/resetPassword", methods=["GET", "POST"])
def resetPasswordPage():
    # POST
    if(request.method == "POST"):
        email = request.form.get("email", None)

        if(email == None):
            return redirect(url_for("loginPage", msg="Niepoprawny adres"))

        username = querySingle(f"SELECT * FROM user WHERE email = '{email}'")[0]

        if(username == None):
            return redirect(url_for("loginPage", msg="Niepoprawny adres"))

        token = getResetToken(username)

        if(token == None):
            return redirect(url_for("loginPage", msg="Niepoprawny adres"))
        
        msg = Message()
        msg.subject = "Reset hasła dla " + username
        msg.recipients = [email]
        msg.sender = GM_USERNAME
        msg.body = render_template("emailResetBody.txt", user=username, token=token)
        msg.html = render_template("emailResetBody.html", user=username, token=token)
    
        mail.send(msg)

        response = redirect(url_for("checkEmailPage"))
        response.set_cookie("email", email)
        return response
    
    # GET
    return render_template("resetPassword.html")
    
@app.route("/login/resetPassword/change/<token>", methods=["GET", "POST"])
def changeResetPasswordPage(token):
    # POST
    if request.method == "POST":
        password = request.form.get("password")
        repPassword = request.form.get("repPassword")
        token = request.form.get("token")

        if password == "" or repPassword == "":
            return render_template("changeResetPassword.html", token=token, msg="Podaj wszystkie dane")
        # Check if passwords match
        if password != repPassword:
            return render_template("changeResetPassword.html", token=token, msg="Hasła muszą być identyczne")

        username = checkToken(token)[0]

        hashed = hashpw(password.encode("utf-8"), gensalt())
        query(f"UPDATE user SET password = '{hashed.decode('utf-8')}' WHERE username = '{username}'")

        return redirect(url_for("loginPage"))

    # GET
    if(token == None):
        redirect(url_for("indexPage"))
    
    if(checkToken(token) == None):
        redirect(url_for("indexPage"))

    return render_template("changeResetPassword.html", token=token)

@app.route("/login/resetPassword/checkEmail", methods=["GET"])
def checkEmailPage():
    email = request.cookies.get("email", None)
    log(email)
    if email == None:
        return redirect(url_for("indexPage"))

    return render_template("checkEmail.html", email=email)


@app.route("/account", methods=["GET"])
@requireLogin
def accountPage():

    user = session.get("login", None)
    if user:
        return render_template("account.html", user=user)
    return redirect(url_for("loginPage"))

@app.route("/account/messages", methods=["GET"])
@requireLogin
def emailPage():
    emails = query(
        f"SELECT * FROM email WHERE toUsername = '{session['login']['username']}'"
    )
    log(emails)
    return render_template("emails.html", emails=emails)

@app.route("/account/messages/newMessage", methods=["GET", "POST"])
@requireLogin
def newEmailPage():

    if request.method == "POST":
        fromUsername = session["login"]["username"]
        toUsername = request.form.get("to")
        topic = request.form.get("topic")
        content = request.form.get("content")

        if (
            len(query(f"SELECT username FROM user WHERE username = '{toUsername}'"))
            == 0
        ):
            return render_template("newEmail.html", msg="Podany adresat nie istnieje", toUsername=toUsername, content=content)
        query(
            f"INSERT INTO email (toUsername, fromUsername, topic, content) VALUES ('{toUsername}', '{fromUsername}', '{topic}', '{content}')"
        )
        return redirect(url_for("emailPage"))

    return render_template("newEmail.html")

@app.route("/account/messages/emails/<id>", methods=["GET"])
@requireLogin
def readEmailPage(id):
    email = querySingle(f"SELECT * FROM email WHERE id = '{id}'")
    if(email == None or email[1] != session["login"]["username"]):
        return redirect(url_for("emailPage"))

    return render_template("readEmail.html", email=email)

@app.route("/account/messages/emails/delete/<id>", methods=["GET"])
@requireLogin
def deleteEmail(id):
    email = querySingle(f"SELECT * FROM email WHERE id = '{id}'")
    if(email == None or email[1] != session["login"]["username"]):
        return redirect(url_for("emailPage"))

    query(f"DELETE FROM email WHERE id = '{email[0]}'")
    return redirect(url_for("emailPage"))

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

@app.route("/cars/info/<id>", methods=["GET"])
@requireLogin
def carInfoPage(id):
    car = querySingle(f"SELECT * FROM car WHERE id = '{id}'")

    return render_template("carInfo.html", car=car)

@app.route("/cars/reserve/<id>", methods=["GET"])
@requireLogin
def carReservePage(id):
    car = querySingle(f"SELECT * FROM car WHERE id = '{id}'")
    username = session["login"]["username"]
    now = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
    id = uuid.uuid4().hex
    log(id)

    query(f"INSERT INTO reservation VALUES ('{id}', '{now}', '{username}', '{car[0]}')")
    res = querySingle(f"SELECT * FROM reservation WHERE id = '{id}'")

    qr = QRCode(version=1, box_size=10, border=1)
    qr.add_data(id)
    qr.make(fit=True)

    img = qr.make_image(fill="black", back_color="white")

    imgData = io.BytesIO()
    img.save(imgData, "png")
    encodedImg=base64.b64encode(imgData.getvalue())

    return render_template("carReserve.html", car=car, res=res, img=encodedImg.decode("utf-8"))

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

@app.route("/github/callback")
def ghCallback():
    if(request.args.get("state") != request.cookies.get("state")):
        return "Nieprawidłowy stan uwierzytelniania.<a href='"+url_for("loginPage")+"'>Spróbuj ponownie</a>"

    params = {
    "client_id": GH_CLIENT_ID,
    "client_secret": GH_CLIENT_SECRET,
    "code": request.args.get("code")
    }
    headers = {
        "Accept" : "application/json"
    }

    tokenResponse = post("https://github.com/login/oauth/access_token", headers=headers, params=params)
    token = json.loads(tokenResponse.text).get("access_token")

    auth = "Bearer " + token

    headers = {
        "Accept" : "application/json",
        "Authorization":auth
    }

    userResponse = get("https://api.github.com/user", headers=headers)
    username = json.loads(userResponse.text).get("login")

    # Jeśli użytkownik GH ma taki sam login jak jakiś użytkownik strony, to będzie problem lol
    userData = querySingle(f"SELECT * FROM user WHERE username = '{username}'")
    log(userData)
    if(userData == None or username != userData[0]):
        psswd = genState()
        hashed = hashpw(psswd.encode("utf-8"), gensalt())
        query(
            f"INSERT INTO user VALUES ('{username}', '{hashed.decode('utf-8')}', 0, 'dawid_b01@wp.pl')"
        )
        session["login"] = User(username, psswd).__dict__

    userData = querySingle(f"SELECT * FROM user WHERE username = '{username}'")
    session["login"] = User(username, userData[2]).__dict__


    return redirect(url_for("indexPage"))

@app.route("/github/auth")
def ghAuth():
    state = genState()
    
    params = {
    "client_id" : GH_CLIENT_ID,
    "redirect_uri": "http://127.0.0.1:5050/github/callback",
    "scope": "repo user",
    "state": state        
    }

    request = Request("GET", "https://github.com/login/oauth/authorize", params=params).prepare()

    response = redirect(request.url)
    response.set_cookie("state", state)

    return response

def genState(l = 30):
  char = ascii_letters + digits
  rand = random.SystemRandom()
  return ''.join(rand.choice(char) for _ in range(l))

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

def getResetToken(username):
    payload = {'reset_password': username, 'exp': datetime.now() + timedelta(seconds=600)}
    return jwt.encode(payload, JWT_KEY, algorithm='HS256')

def checkToken(token):
    try:
        username = jwt.decode(token, JWT_KEY, algorithms=['HS256'])['reset_password']
    except:
        return
    return querySingle(f"SELECT * FROM user WHERE username = '{username}'")
    