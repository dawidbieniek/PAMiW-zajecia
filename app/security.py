from bcrypt import checkpw, gensalt, hashpw
from os import getenv
import datetime
from string import ascii_letters, digits
from random import SystemRandom
import jwt

import mydb

JWT_KEY = None

JWT_EXPIRATION_TIME = datetime.timedelta(seconds=600)
JWT_ALGORITHM = "HS256"


def init():
    global JWT_KEY
    JWT_KEY = getenv("JWT_KEY")


def getResetToken(user):
    payload = {
        "reset_password": user.getUsername(),
        "exp": datetime.datetime.now() + JWT_EXPIRATION_TIME,
    }
    return jwt.encode(payload, JWT_KEY, algorithm=JWT_ALGORITHM)


def checkToken(token):
    from User import User

    if mydb.querySingle(f"SELECT * FROM blackTokens WHERE token = '{token}'") != None:
        return None

    try:
        username = jwt.decode(token, JWT_KEY, algorithms=[JWT_ALGORITHM])[
            "reset_password"
        ]
    except:
        return None
    return User(username)

def blacklistToken(token):    
    tomorrow = (datetime.datetime.now() + datetime.timedelta(days=1)).strftime("%Y/%m/%d %H:%M:%S")
    mydb.querySingle(f"INSERT INTO blackTokens VALUES('{token}', '{tomorrow}')")


def hash(data):
    return hashpw(data.encode("utf-8"), gensalt()).decode("utf-8")


def checkHash(data, hash):
    return checkpw(data.encode("utf-8"), hash.encode("utf-8"))

def genRandomState(l = 30):    
    char = ascii_letters + digits
    rand = SystemRandom()
    return "".join(rand.choice(char) for _ in range(l))
