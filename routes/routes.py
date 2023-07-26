from fastapi import APIRouter, Response, status
from bson import ObjectId, json_util
from pydantic import BaseModel
import json

from models.users import User
from models.book import Book
from config.database import usersCollection, booksCollection, cartCollection, cartItemsCollection
from schema.usersSchemas import listSerialUsers
from schema.bookSchema import listSerialBooks
from utils.passwordHashing import getPasswordHash, verifyPassword
from utils.authentication import createAccessToken, createRefreshToken, getCurrentUser 

router = APIRouter()

@router.get("/", status_code=200)
async def get_users():
    users = listSerialUsers(usersCollection.find())
    return users

@router.post("/signup", status_code=200)
async def signup(user: User, response: Response):
    d = dict(user)
    name = d["name"]
    password = d["password"]
    if usersCollection.find_one({ "name": name }) == None:
        password = getPasswordHash(password)  
        usersCollection.insert_one({ "name": name, "password": password })
        response.status_code = status.HTTP_201_CREATED
        return { "Success": True }
    else:
        response.status_code = status.HTTP_409_CONFLICT
        return { "Success": False, "Error": "User already exists" }

@router.post("/login", status_code=200)
async def login(user: User, response: Response):
    d = dict(user)
    name = d["name"]
    password = d["password"]
    u = usersCollection.find_one({ "name": name })
    if u == None:
        response.status_code = status.HTTP_404_NOT_FOUND
        return { "Success": False, "Error": "Invalid login info" }
    else:
        res = verifyPassword(password, u["password"])
        if res == True:
            jwtToken = await createAccessToken({ "name": name })
            refreshToken = await createRefreshToken({ "name": name })
            response.status_code = status.HTTP_202_ACCEPTED
            return { "Success": True, "jwtToken": jwtToken, "refreshToken": refreshToken }
        else:
            response.status_code = status.HTTP_401_UNAUTHORIZED
            return { "Success": False, "Error": "Invalid login info" }

@router.get("/getBookDetails", status_code=200)
async def getBookDetails(bookId: str, response: Response):
    book = json.loads(json_util.dumps(booksCollection.find_one({ "_id": ObjectId(bookId) })))
    if book == None:
        response.status_code = status.HTTP_404_NOT_FOUND
        return book
    response.status_code = status.HTTP_202_ACCEPTED
    return book

@router.get("/getBooks", status_code=200)
async def getBooks():
    books = listSerialBooks(booksCollection.find())
    return books

@router.post("/addBook", status_code=200)
async def addBook(book: Book, response: Response):
    d = dict(book)
    if booksCollection.find_one({ "title": d["title"] }) == None:
        booksCollection.insert_one(d)
        response.status_code = status.HTTP_201_CREATED
        return { "Success": True }
    else:
        response.status_code = status.HTTP_409_CONFLICT
        return { "Success": False, "Error": "Book already exists" }

@router.get("/cart/getAll", status_code=200)
async def getCart(authToken: str, refreshToken: str, response: Response):
    jwtResponse = await getCurrentUser(authToken, refreshToken)
    if jwtResponse["isRefreshTokenExpired"] == True or jwtResponse["isAuthTokenExpired"] == True:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return jwtResponse
    elif jwtResponse["Error"] == None:
        user = dict(usersCollection.find_one({ "name": jwtResponse["name"] }))
        cart = json.loads(json_util.dumps(cartCollection.find_one({ "user": user })))
        response.status_code = status.HTTP_202_ACCEPTED
        cart["user"]["password"] = None
        return cart
    else:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return jwtResponse

class CartData(BaseModel):
    bookId: str
    authToken: str
    refreshToken: str
    qty: int

@router.post("/cart/add", status_code=200)
async def addCart(data: CartData, response: Response):
    data = dict(data)
    bookId = data["bookId"]
    authToken = data["authToken"]
    refreshToken = data["refreshToken"]
    qty = data["qty"]
    jwtResponse = await getCurrentUser(authToken, refreshToken)
    if jwtResponse["isRefreshTokenExpired"] == True or jwtResponse["isAuthTokenExpired"] == True:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return jwtResponse
    elif jwtResponse["Error"] == None:
        user = dict(usersCollection.find_one({ "name": jwtResponse["name"] }))
        book = booksCollection.find_one({ "_id": ObjectId(bookId) })
        if book == None:
            response.status_code = status.HTTP_400_BAD_REQUEST
            return { "Error": "No such item exists" }
        else:
            cartItem = { "item": book, "qty": qty }
            cart = cartCollection.find_one({ "user": user })
            if cart == None:
                cartItemsCollection.insert_one(cartItem)
                cartItemObj = cartItemsCollection.find_one(cartItem)
                cartCollection.insert_one({ "user": user, "items": [cartItemObj]})
            else:
                #Add more items to cart collection
                cartItems = list(cart["items"])
                flag = False
                for i in range(len(cartItems)):
                    if cartItems[i]["item"]["_id"] == ObjectId(bookId):
                        # Book already exists in cart Item
                        flag = True
                        cartItemsCollection.find_one_and_replace({ "_id": cartItems[i]["_id"] }, { "item": cartItems[i]["item"], "qty": cartItems[i]["qty"] + qty } )
                        x = cartItemsCollection.find_one({ "_id": cartItems[i]["_id"] })
                        #push x to cartItems
                        cartItems[i] = x
                        cartCollection.find_one_and_replace({ "user": user }, { "user": user, "items": cartItems })
                if flag == False:
                    # Book doesn't exist in cart Item
                    cartItemsCollection.insert_one(cartItem)
                    x = cartItemsCollection.find_one(cartItem)
                    #push x to cartItems
                    cartItems.append(x)
                    cartCollection.find_one_and_replace({ "user": user }, { "user": user, "items": cartItems })
            response.status_code = status.HTTP_201_CREATED
            return { "Error": None }
    else:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return jwtResponse

@router.post("/cart/reduce", status_code=200)
async def reduceCart(data: CartData, response: Response):
    data = dict(data)
    bookId = data["bookId"]
    authToken = data["authToken"]
    refreshToken = data["refreshToken"]
    qty = data["qty"]
    jwtResponse = await getCurrentUser(authToken, refreshToken)
    if jwtResponse["isRefreshTokenExpired"] == True or jwtResponse["isAuthTokenExpired"] == True:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return jwtResponse
    elif jwtResponse["Error"] == None:
        user = dict(usersCollection.find_one({ "name": jwtResponse["name"] }))
        book = booksCollection.find_one({ "_id": ObjectId(bookId) })
        if book == None:
            response.status_code = status.HTTP_400_BAD_REQUEST
            return { "Error": "No such item exists" }
        else:
            cart = {}
            if cartCollection.find_one({ "user": user }) != None:
                cart = cartCollection.find_one({ "user": user })
            modified = False
            areQtyEqual = None
            tmp = None
            for i in cart["items"]:
                isBookIdMatching = (ObjectId(bookId) == i["item"]["_id"])
                if isBookIdMatching == True:
                    currentQty = i["qty"]
                    print(f'currentQty -> {currentQty}')
                    if currentQty < qty:
                        return { "Error": "Can't remove more items than existing" }
                    elif currentQty == qty:
                        tmp = cartItemsCollection.find_one_and_delete({ "item": i["item"] })
                        modified = True
                        areQtyEqual = True
                    else:
                        newQty = currentQty - qty
                        cartItemsCollection.find_one_and_replace({ "item": i["item"] }, { "item": i["item"], "qty": newQty })
                        tmp = cartItemsCollection.find_one({ "item": i["item"] })
                        modified = True
                        areQtyEqual = False
            if modified == True:
                cart = cartCollection.find_one({ "user": user })
                items = cart["items"]
                if areQtyEqual == False:
                    for i in range(len(items)):
                        if items[i]["_id"] == tmp["_id"]:
                            cart["items"][i] = tmp
                    cartCollection.find_one_and_replace({ "user": user },cart)
                elif areQtyEqual == True:
                    for i in range(len(items)):
                        if items[i]["_id"] == tmp["_id"]:
                            cart["items"].pop(i)
                            break
                    cartCollection.find_one_and_replace({ "user": user },cart)
            response.status_code = status.HTTP_201_CREATED  
            return { "Error": None }        
    else:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return jwtResponse
    
@router.get("/findBook", status_code=200)
async def findBook(searchStr: str, response: Response):
    books = listSerialBooks(booksCollection.find())
    res = []
    for i in books:
        if i["title"].find(searchStr) != -1 or i["author"].find(searchStr) != -1:
            res.append(i)
    response.status_code = status.HTTP_202_ACCEPTED
    return res