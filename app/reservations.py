from qrcode import QRCode
from base64 import b64encode
from io import BytesIO
import uuid

import mydb

def createId():
    return uuid.uuid4().hex

def add(uuid, now, userId, carId):    
    mydb.query(f"INSERT INTO reservation VALUES ('{uuid}', '{now}', '{userId}', '{carId}')")

def getUsername(uuid):
    return mydb.querySingle(f"SELECT userId FROM reservation WHERE id = '{uuid}'")[0]

def createQRImage(uuid):    
    # Setup qr code generator
    qr = QRCode(version=1, box_size=10, border=1)
    qr.add_data(uuid + getUsername(uuid))
    qr.make(fit=True)
    # Create image
    img = qr.make_image(fill="black", back_color="white")
    # Convert image to base64
    imgData = BytesIO()
    img.save(imgData, "png")
    return b64encode(imgData.getvalue()).decode("utf-8")
