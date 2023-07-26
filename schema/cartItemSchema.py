def individual_serial(cartItem) -> dict:
    return {
        "id": str(cartItem["_id"]),
        "item": cartItem["item"],
        "qty": cartItem["qty"]
    }

def listSerialCartItems(cartItems) -> list:
    return [individual_serial(cartItem) for cartItem in cartItems]