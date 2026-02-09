from datetime import datetime, timedelta
from jose import jwt, JWTError
from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from .config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def create_access_token(data: dict):
    to_encode = {}
    
    # USER ID → TOKEN'A sub olarak yazılmak zorunda!
    to_encode["sub"] = str(data.get("user_id"))

    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode["exp"] = expire

    print("🔑 CREATE TOKEN PAYLOAD:", to_encode)

    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        print("🔍 DECODED TOKEN:", payload)   # <---- Bunu ekle
        return payload
    except JWTError:
        raise HTTPException(401, "Invalid or expired token")
