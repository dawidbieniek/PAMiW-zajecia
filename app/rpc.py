import requests
import json

import uuid

url = "http://10.5.0.11:4000/jsonrpc"
headers = {'content-type': 'application/json'}

def createReservation(time, userId, carId):
    payload = {
        "method": "add",
        "params": [time, userId, carId],
        "jsonrpc": "2.0",
        "id": 0,
    }
    response = requests.post(url, data=json.dumps(payload), headers=headers).json()

    return response["result"]

def getReservation(id):
    payload = {
        "method": "get",
        "params": [id],
        "jsonrpc": "2.0",
        "id": 0,
    }
    response = requests.post(url, data=json.dumps(payload), headers=headers).json()
    resp = response.get("result", None)
    return resp != None
