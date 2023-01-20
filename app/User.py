from security import hash, checkHash
import mydb

class User:
    def __init__(self, username):
        self.username = username

    def getUsername(self):
        return self.username

    def getEmail(self):
        return self.queryField("email")

    def isAdmin(self):
        return self.queryField("isadmin") == 1

    def checkPassword(self, password):
        hashed = self.queryField("password")
        if not hashed:
            return None
        return checkHash(password, hashed)

    def changePassword(self, password):
        hashed = hash(password)
        mydb.query(
            f"UPDATE user SET password = '{hashed}' WHERE username = '{self.username}'"
        )

    def register(self, email, password):
        hashed = hash(password)
        mydb.query(
            f"INSERT INTO user VALUES ('{self.username}', '{email}', '{hashed}', 0)"
        )

    @staticmethod
    def fromEmail(email):
        username = mydb.querySingle(f"SELECT username FROM user WHERE email = '{email}'")[
            0
        ]
        if not username:
            return None
        return User(username)

    def queryField(self, field):
        row = mydb.querySingle(f"SELECT {field} FROM user WHERE username = '{self.username}'")
        if not row:
            return None
        return row[0]


def isLoginTaken(username):
    return mydb.querySingle(f"SELECT * FROM user WHERE username = '{username}'") != None


def isEmailTaken(email):
    return mydb.querySingle(f"SELECT * FROM user WHERE email = '{email}'") != None

def getAllUsers():
    return mydb.query("SELECT * FROM user")
