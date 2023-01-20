from werkzeug.wrappers import Request, Response
from werkzeug.serving import run_simple
from jsonrpc import JSONRPCResponseManager, dispatcher
import uuid

import mydb

def createId():
    return uuid.uuid4().hex

def addReservation(time, userId, carId):
    id = createId()
    mydb.query(f"INSERT INTO reservation VALUES ('{id}', '{time}', '{userId}', '{carId}')")
    return id

def getReservation(id):
    res = mydb.querySingle(f"SELECT id FROM reservation WHERE id = '{id}'")
    if res:
        return res[0]
    return None

@Request.application
def application(request):
    dispatcher["add"] = addReservation
    dispatcher["get"] = getReservation

    response = JSONRPCResponseManager.handle(
        request.get_data(cache=False, as_text=True), dispatcher)
    return Response(response.json, mimetype='application/json')

if __name__ == '__main__':
    run_simple('10.5.0.11', 4000, application)
