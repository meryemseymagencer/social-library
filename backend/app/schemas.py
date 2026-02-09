# Bu dosya, API’ye gelen verilerin tiplerini belirler.
from pydantic import BaseModel, Field, EmailStr
from datetime import datetime
# ——— REGISTER İÇİN ——— #
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
# ——— LOGIN İÇİN ——— #
class UserLogin(BaseModel):
    email: EmailStr
    password: str
# ——— CEVAP MODELİ ——— #
class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    avatar_url: str | None = None
    bio: str | None = None
    created_at: datetime

    is_me: bool
    is_following: bool

    followers_count: int
    following_count: int

    class Config:
        from_attributes = True

# ——— TOKEN MODELLERİ ——— #
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
# ——— KULLANICI GÜNCELLEME İÇİN ——— #
class UserUpdate(BaseModel):
    username: str | None = None
    bio: str | None = None
    avatar_url: str | None = None
# ——— TAKİPÇİ / TAKİP EDİLEN MODELİ ——— #
class FollowUser(BaseModel):
    id: int
    username: str
    avatar_url: str | None = None

    class Config:
     from_attributes = True
# ——— RATING YORUMU oluşturma ve özeti ——— #
class RatingCreate(BaseModel):
    score: int = Field(..., ge=1, le=5) # 1–5 arası zorunlu
class RatingSummary(BaseModel):
    average: float | None = None
    count: int
    user_score: int | None = None
class ReviewCreate(BaseModel):
    content: str
class ReviewResponse(BaseModel):
    id: int
    user_id: int
    item_id: int
    content: str
    created_at: datetime
    updated_at: datetime | None = None

    class Config:
        from_attributes = True
# --- LİSTE ITEM ÖZETİ (FRONTEND İÇİN) ---
class ItemSummary(BaseModel):
    id: int
    title: str
    year: int | None = None
    poster_url: str | None = None

    class Config:
        from_attributes = True
# --- LİSTE OLUŞTURMA ---
class ListCreate(BaseModel):
    name: str
    description: str | None = None
# --- LİSTE GÜNCELLEME ---
class ListUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
# --- LİSTE CEVABI (ARTIK TAM DETAYLAR İLE) ---
class ListResponse(BaseModel):
    id: int
    user_id: int
    name: str
    description: str | None
    is_system: bool
    item_count: int
    items: list[ItemSummary]

    class Config:
        from_attributes = True
        