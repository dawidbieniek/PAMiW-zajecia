from flask import (
    Flask,
    request,
    Response,
    render_template,
    url_for,
    redirect,
    session,
    send_from_directory,
)
from dotenv import load_dotenv
from os import path, remove

from datetime import datetime
import secrets
import functools

from User import User, isLoginTaken, isEmailTaken, getAllUsers
import mydb
import security
import myemail
import message
import cars
import rpc
import auth
import qr

from debug import log

load_dotenv()


app = Flask(__name__)

app.jinja_env.line_statement_prefix = "#"

app.config["UPLOAD_FOLDER"] = "/tmp/"

app.config["SESSION_PERMANENT"] = False
app.config["SECRET_KEY"] = secrets.token_urlsafe(16)

security.init()
auth.init()
myemail.init(app)


def requireLogin(func):
    @functools.wraps(func)
    def secureFunction(*args, **kwargs):
        if not isLoggedin():
            return redirect(url_for("loginPage", next=request.url))
        return func(*args, **kwargs)

    return secureFunction

def requireAdmin(func):
    @functools.wraps(func)
    def internal(*args, **kwargs):
        if not isCurrentUserAdmin():
            return "Brak uprawnień <br> <a href='" + url_for("indexPage") + "'>Strona główna</a>"
        return func(*args, **kwargs)

    return internal

def prohibitLogged(func):
    @functools.wraps(func)
    def internal(*args, **kwargs):
        if isLoggedin():
            return redirect(url_for("indexPage"))
        return func(*args, **kwargs)

    return internal

@app.route("/")
def indexPage():
    return render_template("index.html")


@app.route("/logout", methods=["GET"])
def logout():
    if session.get("login", None) != None:
        session.clear()
    return redirect(url_for("indexPage"))


@app.route("/login", methods=["GET", "POST"])
@prohibitLogged
def loginPage():
    # POST
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        nextUrl = request.form.get("next", None)

        # Check if form had all fields
        if not username or not password:
            return render_template(
                "login.html",
                msg="Podaj login i hasło",
                username=(username if username else None),
            )

        user = User(username)
        log(user)
        if user.checkPassword(password):
            # Save user to session
            session["login"] = username
            # Redirect
            if nextUrl:
                return redirect(nextUrl)
            return redirect(url_for("indexPage"))

        return render_template(
            "login.html", msg="Niepoprawne dane logowania", username=username
        )
    # GET
    msg = request.args.get("msg", None)
    if msg:
        return render_template("login.html", msg=msg)
    else:
        return render_template("login.html", next=request.args.get("next", ""))


@app.route("/login/register", methods=["GET", "POST"])
@prohibitLogged
def registerPage():
    # POST
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        repPassword = request.form.get("repPassword")

        # Check if form had all fields
        if not username or not email or not password or not repPassword:
            return render_template(
                "register.html",
                msg="Podaj wszystkie dane",
                username=(username if username else None),
                email=(email if email else None),
            )
        # Check if passwords match
        if password != repPassword:
            return render_template(
                "register.html", msg="Hasła muszą być identyczne", username=username, email=email
            )
        # Check if login already exists
        if isLoginTaken(username):
            return render_template(
                "register.html", msg="Login już jest zajęty", username=username, email=email
            )
        # Check if email already exists
        if isEmailTaken(username):
            return render_template(
                "register.html", msg="Email już jest zajęty", username=username, email=email
            )
        # Register user
        User(username).register(email, password)
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

        # Check if form had all fields
        if not password or not newPassword or not repNewPassword:
            return render_template("changePassword.html", msg="Podaj wszystkie dane")
        # Check if passwords match
        if newPassword != repNewPassword:
            return render_template(
                "changePassword.html", msg="Nowe hasła muszą być identyczne"
            )
        # Check if new password is different than current one
        if newPassword == password:
            return render_template(
                "changePassword.html", msg="Nowe hasło musi różnić się od starego"
            )
        # Check if old password is correct
        user = User(session["login"])
        if not user.checkPassword(password):
            return render_template("changePassword.html", msg="Niepoprawne hasło")
        # Update password
        user.changePassword(newPassword)
        return redirect(url_for("loginPage"))
    # GET
    return render_template("changePassword.html")


@app.route("/login/resetPassword", methods=["GET", "POST"])
def resetPasswordPage():
    # POST
    if request.method == "POST":
        email = request.form.get("email", None)

        # Check if form had all fields
        if not email:
            return redirect(url_for("loginPage", msg="Niepoprawny adres email"))

        # Check if email in connected to registered user
        user = User.fromEmail(email)
        if not user:
            return redirect(url_for("loginPage", msg="Niepoprawny adres"))

        # Create token
        token = security.getResetToken(user)
        if not token:
            return redirect(url_for("loginPage", msg="Niepoprawny adres"))

        # Send email
        username = user.getUsername()
        myemail.sendEmail(
            "Reset hasła dla " + username,
            email,
            render_template("emailResetBody.txt", user=username, token=token),
            render_template("emailResetBody.html", user=username, token=token),
        )
        # TODO zmienić z ciasteczek na parametry URL
        response = redirect(
            url_for(
                "checkEmailPage",
            )
        )
        response.set_cookie("email", email)
        return response

    # GET
    return render_template("resetPassword.html")


# TODO sprawdzić czy przesyłanie tokena w GET ma sens
@app.route("/login/resetPassword/change/<token>", methods=["GET", "POST"])
def changeResetPasswordPage(token):
    # POST
    if request.method == "POST":
        password = request.form.get("password")
        repPassword = request.form.get("repPassword")
        token = request.form.get("token")

        # Check if form had all fields
        if not password or not repPassword:
            return render_template(
                "changeResetPassword.html", token=token, msg="Podaj wszystkie dane"
            )
        # Check if passwords match
        if password != repPassword:
            return render_template(
                "changeResetPassword.html",
                token=token,
                msg="Hasła muszą być identyczne",
            )

        # Change password
        user = security.checkToken(token)
        if user:
            user.changePassword(password)
            security.blacklistToken(token)
        else:
            return redirect(url_for("indexPage"))

        return redirect(url_for("loginPage"))

    # GET
    if not token or not security.checkToken(token):
        return redirect(url_for("indexPage"))

    return render_template("changeResetPassword.html", token=token)


@app.route("/login/resetPassword/checkEmail", methods=["GET"])
def checkEmailPage():
    email = request.cookies.get("email", None)

    if not email:
        return redirect(url_for("indexPage"))

    return render_template("checkEmail.html", email=email)


@app.route("/account", methods=["GET", "POST"])
@requireLogin
def accountPage():
    # POST
    if request.method == "POST":
        file = request.files.get("file", None)
        filePath = path.join(app.config["UPLOAD_FOLDER"], session["login"] + ".png")

        if path.exists(filePath):
            remove(filePath)

        file.save(filePath)
    # GET
    user = User(session.get("login", None))
    if user:
        return render_template("account.html", user=user.getUsername(), email=user.getEmail(), admin=user.isAdmin())
    return redirect(url_for("loginPage"))


@app.route("/account/upload/", methods=["GET"])
@requireLogin
def uploadPage():
    return send_from_directory(app.config["UPLOAD_FOLDER"], session["login"] + ".png")


@app.route("/account/messages", methods=["GET"])
@requireLogin
def emailPage():
    emails = mydb.query(
        f"SELECT * FROM message WHERE toUsername = '{session['login']}'"
    )
    return render_template("emails.html", emails=emails)


@app.route("/account/messages/newMessage", methods=["GET", "POST"])
@requireLogin
def newEmailPage():
    # POST
    if request.method == "POST":
        toUsername = request.form.get("to")
        topic = request.form.get("topic")
        content = request.form.get("content")

        if not isLoginTaken(toUsername):
            return render_template(
                "newEmail.html",
                msg="Podany adresat nie istnieje",
                toUsername=toUsername,
                content=content,
            )

        message.addMessage(session["login"], toUsername, topic, content)
        return redirect(url_for("emailPage"))
    # GET
    return render_template("newEmail.html")


@app.route("/account/messages/emails/<id>", methods=["GET"])
@requireLogin
def readEmailPage(id):
    email = message.getMessage(session["login"], id)
    if not email:
        redirect(url_for("emailPage"))

    return render_template(
        "readEmail.html",
        fromName=email[0],
        subject=email[1],
        body=email[2],
        id=email[3],
    )


@app.route("/account/messages/emails/delete/<id>", methods=["GET"])
@requireLogin
def deleteEmail(id):
    message.deleteMessage(session["login"], id)
    return redirect(url_for("emailPage"))


@app.route("/carSearch", methods=["GET", "POST"])
def carSearchPage():
    # POST
    if request.method == "POST":
        text = request.get_json().get("query")
        if text:
            carsTable = cars.getCarsLike(text)
        else:
            carsTable = cars.getAllCars()
        return render_template("tables/carTable.html", cars=carsTable)

    # GET
    return render_template("carSearch.html")


@app.route("/cars/info/<id>", methods=["GET"])
@requireLogin
def carInfoPage(id):
    car = cars.getCarInfo(id)

    if not car:
        return redirect(url_for('searchPage'))

    return render_template("carInfo.html", car=car)

@app.route("/cars/reserve/<id>", methods=["GET"])
@requireLogin
def carReservePage(id):
    username = session["login"]
    now = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
    car = cars.getCarInfo(id)

    if not car:
        return redirect(url_for("searchPage"))
    reservationId = rpc.createReservation(now, username, car[0])

    return render_template("carReserve.html", car=car, resId=reservationId, img=qr.createQRImage(reservationId))


@app.route("/userList", methods=["GET"])
@requireAdmin
def userListPage():
    return render_template("userList.html", users=getAllUsers())


@app.route("/api/messageCount")
@requireLogin
def apiMessageCount():
    numberOfMsgs = mydb.querySingle(
        f"SELECT COUNT(*) FROM message WHERE toUsername = '{session['login']}'"
    )[0]
    return str(numberOfMsgs)


@app.route("/api/isLoggedIn")
def apiLoggedIn():
    return str(isLoggedin())
    
@app.route("/api/isAdmin")
def apiAdmin():
    return str(isCurrentUserAdmin())

@app.route("/api/cars/reserve/downloadQr", methods=["POST"])
def downloadQr():
    if request.method == "POST":
        imgData = request.form.get("imgData")
        qrImg = qr.createPlainQRImage(imgData)
        generator = (qrImg)
        return Response(generator, mimetype="image.png", headers={"Content-Disposition" : "attachment;filename=reservation.png"})
    return redirect(url_for('indexPage'))


@app.route("/github/callback")
def ghCallback():
    if request.args.get("state") != request.cookies.get("state"):
        return (
            "Nieprawidłowy stan uwierzytelniania.<a href='"
            + url_for("loginPage")
            + "'>Spróbuj ponownie</a>"
        )
        
    userData = auth.GHGetUserData(request)

    # Jeśli użytkownik GH ma taki sam login jak jakiś użytkownik strony, to będzie problem lol
    user = auth.GHRegisterNewUser(userData[0], userData[1])
    session["login"] = user.getUsername()

    return redirect(url_for("indexPage"))


@app.route("/github/auth")
def ghAuth():    
    return auth.GHAuthResponse()


def isLoggedin():
    return session.get("login", None) != None


def isCurrentUserAdmin():
    if not isLoggedin():
        return False

    return User(session["login"]).isAdmin()