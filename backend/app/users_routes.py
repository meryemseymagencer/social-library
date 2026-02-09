from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from uuid import uuid4
import os

from .database import get_db
from .security import get_current_user
from . import models
from .models import User, Review, Item, UserList
from .schemas import FollowUser, UserResponse, UserUpdate

router = APIRouter(prefix="/users", tags=["Users"])

# =====================
# ORTAK RESPONSE BUILDER
# =====================
def build_user_response(user: User, current_user: User, db: Session):
    from .models import Follow

    followers_count = len(user.followers)
    following_count = len(user.following)

    # current_user, 'user'ı takip ediyor mu?
    is_following = db.query(Follow).filter(
        Follow.follower_id == current_user.id,
        Follow.following_id == user.id
    ).first() is not None

    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "avatar_url": user.avatar_url,
        "bio": user.bio,
        "created_at": user.created_at,

        "is_me": (user.id == current_user.id),
        "is_following": is_following,
        "followers_count": followers_count,
        "following_count": following_count,
    }


# =====================
# ME ENDPOINTLERİ
# =====================
@router.get("/me", response_model=UserResponse)
def get_my_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Kendimiz için response
    return build_user_response(current_user, current_user, db)

@router.put("/me", response_model=UserResponse)
def update_my_profile(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if user_update.username is not None:
        current_user.username = user_update.username

    if user_update.bio is not None:
        current_user.bio = user_update.bio

    db.commit()
    db.refresh(current_user)

    return build_user_response(current_user, current_user, db)

@router.get("/me/followers", response_model=list[FollowUser])
def get_my_followers(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return get_followers(current_user.id, db)


@router.get("/me/following", response_model=list[FollowUser])
def get_my_following(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return get_following(current_user.id, db)


@router.get("/me/posts")
def get_my_posts(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return _get_user_posts(current_user.id, db)


@router.get("/me/reviews")
def get_my_reviews(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return _get_user_reviews(current_user.id, db)


# =====================
# BAŞKA KULLANICILAR
# =====================

@router.get("/{id}/posts")
def get_user_posts(id: int, db: Session = Depends(get_db)):
    return _get_user_posts(id, db)


@router.get("/{id}/reviews")
def get_user_reviews(id: int, db: Session = Depends(get_db)):
    return _get_user_reviews(id, db)


@router.get("/{id}/lists")
def get_user_lists(id: int, db: Session = Depends(get_db)):
    """
    Kullanıcının listelerini getirir.
    """
    return _get_user_lists(id, db)


@router.get("/{id}/followers", response_model=list[FollowUser])
def get_followers(id: int, db: Session = Depends(get_db)):
    followers = (
        db.query(User)
        .join(models.Follow, models.Follow.follower_id == User.id)
        .filter(models.Follow.following_id == id)
        .all()
    )
    return followers


@router.get("/{id}/following", response_model=list[FollowUser])
def get_following(id: int, db: Session = Depends(get_db)):
    following = (
        db.query(User)
        .join(models.Follow, models.Follow.following_id == User.id)
        .filter(models.Follow.follower_id == id)
        .all()
    )
    return following


@router.get("/{id}", response_model=UserResponse)
def get_user_profile(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    user = db.query(User).filter(User.id == id).first()
    if not user:
        raise HTTPException(404, "User not found")

    # Başkasının profilini görüntülerken de aynı builder
    return build_user_response(user, current_user, db)


# =====================
# YARDIMCI SORGULAR
# =====================

def _get_user_posts(user_id: int, db: Session):
    q = (
        db.query(Item)
        .join(Review, Review.item_id == Item.id)
        .filter(Review.user_id == user_id)
        .group_by(Item.id)
        .order_by(Item.created_at.desc())
        .all()
    )

    return [
        {
            "id": item.id,
            "poster_url": item.poster_url,
            "title": item.title,
        }
        for item in q
    ]


def _get_user_reviews(user_id: int, db: Session):
    q = (
        db.query(Review, Item)
        .join(Item, Review.item_id == Item.id)
        .filter(Review.user_id == user_id)
        .order_by(Review.created_at.desc())
        .all()
    )

    result = []
    for review, item in q:
        result.append(
            {
                "id": review.id,
                "item_id": item.id,
                "item_title": item.title,
                "poster_url": item.poster_url,
                "review_text": review.content,
                "created_at": review.created_at,
            }
        )
    return result


def _get_user_lists(user_id: int, db: Session):
    lists = (
        db.query(UserList)
        .filter(UserList.user_id == user_id)
        .order_by(UserList.id.desc())
        .all()
    )

    return [
        {
            "id": lst.id,
            "name": lst.name,
            "description": lst.description,
            "is_system": lst.is_system,
        }
        for lst in lists
    ]


# =====================
# AVATAR YÜKLEME
# =====================

AVATAR_DIR = "static/avatars"
os.makedirs(AVATAR_DIR, exist_ok=True)


@router.post("/me/avatar")
def upload_avatar(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    ext = file.filename.split(".")[-1].lower()
    filename = f"{uuid4()}.{ext}"
    filepath = os.path.join(AVATAR_DIR, filename)

    with open(filepath, "wb") as buffer:
        buffer.write(file.file.read())

    AVATAR_BASE = "http://localhost:8000"

    avatar_url = f"{AVATAR_BASE}/static/avatars/{filename}"



    current_user.avatar_url = avatar_url
    db.commit()
    db.refresh(current_user)

    return {"avatar_url": avatar_url}
