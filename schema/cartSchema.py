def individual_serial(cartI) -> dict:
    return {
        "id": str(cartI["_id"]),
        "user": cartI["user"],
        "items": cartI["items"]
    }

def listSerialCarts(cart) -> list:
    return [individual_serial(cartItem) for cartItem in cart]
