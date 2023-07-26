from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext

from .token import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_HOURS

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def createAccessToken(data: dict):
    to_encode = data.copy()
    expire = (datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)).timestamp()
    to_encode.update({"auth": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def createRefreshToken(data: dict):
    to_encode = data.copy()
    expire = (datetime.utcnow() + timedelta(hours=REFRESH_TOKEN_EXPIRE_HOURS)).timestamp()
    to_encode.update({"refresh": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def getCurrentUser(authToken: str, refreshToken: str):
    try:
        payload = jwt.decode(authToken, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload["name"]
        authTime = payload["auth"]
        currentTimestamp = datetime.utcnow().timestamp()
        authFlag = currentTimestamp < authTime
        if authFlag == False:
            #JWTToken Expired
            refreshPayload = jwt.decode(refreshToken, SECRET_KEY, algorithms=[ALGORITHM])
            refreshTime = refreshPayload["refresh"]
            refreshFlag = currentTimestamp < refreshTime
            if refreshFlag == False:
                #RefreshToken Expired
                return { "Error": "Token expired", "isAuthTokenExpired": True, "isRefreshTokenExpired": True }
            else:
                authToken = await createAccessToken({ "name": payload["name"] })
                return { "Error": "Token expired", "isAuthTokenExpired": True, "isRefreshTokenExpired": False, "authToken": authToken }
        if username is None:
            return { "Error": "No users matched", "isAuthTokenExpired": False, "isRefreshTokenExpired": False }
        return { "Error": None, "name": username, "isAuthTokenExpired": False, "isRefreshTokenExpired": False }
    except JWTError:
        return { "Error": "Invalid token", "isAuthTokenExpired": False, "isRefreshTokenExpired": False }