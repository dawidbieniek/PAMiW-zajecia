from flask import (
    Flask,
    request,
    render_template,
)

import rpc
import qr

app = Flask(__name__)

app.jinja_env.line_statement_prefix = "#"

@app.route("/", methods=["GET", "POST"])
def indexPage():
    # POST
    if request.method == "POST":
        textId = request.form.get("textId")
        qrCode = request.files.get("qr", None)
        
        id = None

        if textId:
            id = rpc.getReservation(textId)
        if qrCode:
            id = qr.decodeQRImage(qrCode.read())
            
        if not id:
            return render_template("index.html", msg="Zły id rezerwacji")

        good = rpc.getReservation(id)
        
        if good:
            return render_template("index.html", msg="OK!", id=id)
            
        return render_template("index.html", msg="Zły id rezerwacji")

        
    # GET
    return render_template("index.html")
