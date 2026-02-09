from passlib.context import CryptContext
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.security import HTTPBearer
from jose import jwt, JWTError

from .database import get_db
from .models import User
from .jwt_handler import decode_access_token
from .config import SECRET_KEY, ALGORITHM

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)
def get_current_user(
    token: dict = Depends(decode_access_token),
    db: Session = Depends(get_db)
):
    # Token dictionary şeklinde geliyor mu?
    print("🔥 TOKEN GET_CURRENT_USER:", token)

    # Token içinden user id çek
    user_id = token.get("sub")

    if not user_id:
        raise HTTPException(401, "Token does not contain user ID (sub)")

    user = db.query(User).filter(User.id == int(user_id)).first()

    if not user:
        raise HTTPException(404, "User not found")

    return user

# OPSİYONEL kullanıcı (giriş yapmak zorunda değil)
security = HTTPBearer(auto_error=False)

def get_optional_user(
    token: str = Depends(security),
    db: Session = Depends(get_db)
):
    if not token:
        return None

    try:
        payload = jwt.decode(token.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if not user_id:
            return None

        return db.query(User).filter(User.id == int(user_id)).first()
    except JWTError:
        return None
