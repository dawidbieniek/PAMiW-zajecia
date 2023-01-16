import mydb


def addMessage(fromName, toName, subject, body):
    mydb.query(
        f"INSERT INTO message (toUsername, fromUsername, topic, content) VALUES ('{toName}', '{fromName}', '{subject}', '{body}')"
    )

def getMessage(username, id):
    data = mydb.querySingle(f"SELECT toUsername, fromUsername, topic, content FROM message WHERE id = '{id}'")
    if not data or data[0] != username:
        return None
    return data[1:] + (id,)

def deleteMessage(username, id):
    data = mydb.querySingle(f"SELECT toUsername FROM message WHERE id = '{id}'")
    if not data or data[0] != username:
        return None
        
    mydb.query(f"DELETE FROM message WHERE id = '{id}'")
