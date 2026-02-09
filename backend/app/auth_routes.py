from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .database import SessionLocal
from . import models
from .schemas import UserCreate, UserLogin, UserResponse, Token
from .security import hash_password, verify_password
from .jwt_handler import create_access_token

router = APIRouter(tags=["Auth"])
# DB dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

from datetime import datetime, timedelta
from random import randint
from .utils.send_email import send_reset_code

@router.post("/request-reset")
def request_reset(email: str, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user:
        raise HTTPException(400, "Böyle bir e-posta yok")

    # 6 haneli kod
    code = f"{randint(100000, 999999)}"

    user.reset_code = code
    user.reset_code_expires = datetime.utcnow() + timedelta(minutes=5)

    db.commit()

    send_reset_code(user.email, code)

    return {"detail": "reset_code_sent"}
@router.post("/verify-reset-code")
def verify_reset_code(email: str, code: str, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user:
        raise HTTPException(400, "E-posta bulunamadı")

    if user.reset_code != code:
        raise HTTPException(400, "Kod yanlış")

    if user.reset_code_expires < datetime.utcnow():
        raise HTTPException(400, "Kodun süresi doldu")

    return {"detail": "code_valid"}
from .security import hash_password

@router.post("/set-new-password")
def set_new_password(email: str, code: str, new_password: str, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user:
        raise HTTPException(400, "E-posta bulunamadı")

    if user.reset_code != code:
        raise HTTPException(400, "Kod geçersiz")

    if user.reset_code_expires < datetime.utcnow():
        raise HTTPException(400, "Kodun süresi doldu")

    # Yeni şifre kaydedilir
    user.password_hash = hash_password(new_password)
    user.reset_code = None
    user.reset_code_expires = None

    db.commit()

    return {"detail": "password_updated"}

# ——— REGISTER ——— #
@router.post("/register", response_model=UserResponse)
def register(user: UserCreate, db: Session = Depends(get_db)):

    # Email kontrol
    existing_user = db.query(models.User).filter(models.User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Username kontrol
    existing_username = db.query(models.User).filter(models.User.username == user.username).first()
    if existing_username:
        raise HTTPException(status_code=400, detail="Username already exists")

    # Şifre hash
    hashed_pw = hash_password(user.password)

    # Yeni user oluştur
    new_user = models.User(
        username=user.username,
        email=user.email,
        password_hash=hashed_pw
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # ───────────────────────────────
    #  SİSTEM LİSTELERİNİ OLUŞTUR 
    default_lists = [
        ("Okudum", "Okuduğun kitaplar"),
        ("Okuyacağım", "Okumayı düşündüğün kitaplar"),
        ("İzledim", "İzlediğin filmler"),
        ("İzleyeceğim", "İzlemeyi düşündüğün filmler"),
    ]

    for name, desc in default_lists:
        new_list = models.UserList(
            user_id=new_user.id,
            name=name,
            description=desc
        )
        db.add(new_list)

    db.commit()

    # ───────────────────────────────

    # Cevap döndür
    return {
        "id": new_user.id,
        "username": new_user.username,
        "email": new_user.email,
        "avatar_url": new_user.avatar_url,
        "bio": new_user.bio,
        "created_at": new_user.created_at,
        "is_me": True,
        "is_following": False,
        "followers_count": 0,
        "following_count": 0,
    }

# ——— LOGIN ——— #
@router.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):

    # 1. Kullanıcı var mı?
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if not db_user:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    # 2. Şifre doğru mu?
    if not verify_password(user.password, db_user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    # 3. Token oluştur
    access_token = create_access_token({"user_id": db_user.id})

    # 4. UserResponse modeli ile kullanıcı bilgisi
    user_data = {
        "id": db_user.id,
        "username": db_user.username,
        "email": db_user.email,
        "avatar_url": db_user.avatar_url,
        "bio": db_user.bio
    }

    return {
        "access_token": access_token,
        "user": user_data
    }
