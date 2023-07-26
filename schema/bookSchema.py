def individual_serial(book) -> dict:
    return {
        "id": str(book["_id"]),
        "title": book["title"],
        "author": book["author"],
        "description": book["description"],
        "price": float(book["price"]),
        "imgUrl": book["imgUrl"]
    }

def listSerialBooks(books) -> list:
    return [individual_serial(book) for book in books]