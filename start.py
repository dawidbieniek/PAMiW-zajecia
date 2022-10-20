import time
from flask import Flask
from flask import request
from flask import make_response
from flask import render_template

app = Flask(__name__)

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/login.html')
def loginPage():
    return render_template("login.html")
    
@app.route('/search.html')
def searchPage():
    return render_template("search.html")

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5050)