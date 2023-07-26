def individual_serial(user) -> dict:
    return {
        "id": str(user["_id"]),
        "name": user["name"],
        "password": user["password"]
    }

def listSerialUsers(users) -> list:
    return [individual_serial(user) for user in users]