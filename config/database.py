from pymongo.mongo_client import MongoClient

from DBCredentials.db import username, password

uri = f"mongodb+srv://{username}:{password}@cluster0.a6v81ie.mongodb.net/?retryWrites=true&w=majority"
#Create a new client and connect to the server
client = MongoClient(uri)
#Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:  
    print("Database Exception")
    print(e)

db = client.books

usersCollection = db["users_collection"]
booksCollection = db["books_collection"]
cartCollection = db["cart_collection"]
cartItemsCollection = db["cart_items_collection"]