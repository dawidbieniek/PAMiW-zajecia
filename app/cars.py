import mydb

def getAllCars():
    return mydb.query(f"SELECT * FROM car")
    
def getCarsLike(text):
    return mydb.query(f"SELECT * FROM car WHERE carName LIKE '%{text}%'")

def getCarInfo(id):
    return mydb.querySingle(f"SELECT * FROM car WHERE id = '{id}'")