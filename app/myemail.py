from os import getenv
from flask_mail import Mail, Message

GM_USERNAME = None
GM_PASSWORD = None

mail = None

def init(app):
    global GM_USERNAME 
    GM_USERNAME = getenv("GM_USERNAME")
    global GM_PASSWORD 
    GM_PASSWORD = getenv("GM_PASSWORD")

    app.config["MAIL_SERVER"] = "smtp.gmail.com"
    app.config["MAIL_PORT"] = 465
    app.config["MAIL_USE_SSL"] = True
    app.config["MAIL_USERNAME"] = GM_USERNAME
    app.config["MAIL_PASSWORD"] = GM_PASSWORD

    global mail 
    mail = Mail(app)


def sendEmail(subject, recipient, body, html):
    msg = Message()
    msg.subject = subject
    msg.recipients = [recipient]
    msg.sender = GM_USERNAME
    msg.body = body
    msg.html = html

    mail.send(msg)
