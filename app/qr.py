from qrcode import QRCode
from base64 import b64encode
from io import BytesIO
from pyzbar.pyzbar import decode
from PIL import Image

def createQRImage(data):    
    # Setup qr code generator
    qrImg = QRCode(version=1, box_size=10, border=1)
    qrImg.add_data(data)
    qrImg.make(fit=True)
    # Create image
    img = qrImg.make_image(fill="black", back_color="white")
    # Convert image to base64
    imgData = BytesIO()
    img.save(imgData, "png")
    return b64encode(imgData.getvalue()).decode("utf-8")


def createPlainQRImage(data):    
    # Setup qr code generator
    qrImg = QRCode(version=1, box_size=10, border=1)
    qrImg.add_data(data)
    qrImg.make(fit=True)
    # Create image
    img = qrImg.make_image(fill="black", back_color="white")
    # Convert image to base64
    imgData = BytesIO()
    img.save(imgData, "png")
    return imgData.getvalue()


def decodeQRImage(data):
    return decode(Image.open(BytesIO(data)))[0].data.decode("utf-8")