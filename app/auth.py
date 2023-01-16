from flask import redirect
from requests import Request, post, get
from os import getenv
from json import loads

from security import genRandomState
from User import User, isLoginTaken

GH_CLIENT_ID = None
GH_CLIENT_SECRET = None

def init():
    global GH_CLIENT_ID 
    GH_CLIENT_ID = getenv("CLIENT_ID")
    global GH_CLIENT_SECRET
    GH_CLIENT_SECRET = getenv("CLIENT_SECRET")

def GHAuthResponse():
    state = genRandomState()

    params = {
        "client_id": GH_CLIENT_ID,
        "redirect_uri": "http://127.0.0.1:5050/github/callback",
        "scope": "repo user",
        "state": state,
    }

    request = Request(
        "GET", "https://github.com/login/oauth/authorize", params=params
    ).prepare()

    response = redirect(request.url)
    response.set_cookie("state", state)

    return response

def GHGetUserData(request):    
    params = {
        "client_id": GH_CLIENT_ID,
        "client_secret": GH_CLIENT_SECRET,
        "code": request.args.get("code"),
    }
    headers = {"Accept": "application/json"}

    tokenResponse = post(
        "https://github.com/login/oauth/access_token", headers=headers, params=params
    )
    token = loads(tokenResponse.text).get("access_token")
    auth = "Bearer " + token
    headers = {"Accept": "application/json", "Authorization": auth}

    userResponse = get("https://api.github.com/user", headers=headers)
    return (loads(userResponse.text).get("login"), "placeholder")

def GHReqisterNewUser(username, email):
    user = User(username)
    if not isLoginTaken(username):
        user.register(email, genRandomState())