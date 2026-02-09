# app/follow_routes.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .database import get_db
from .models import Follow, User
from .security import get_current_user
router = APIRouter(prefix="/follow", tags=["Follow"])
# ---- Takip Et ---- #
@router.post("/{user_id}")
def follow_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if user_id == current_user.id:
        raise HTTPException(400, "Kendinizi takip edemezsiniz.")

    # Kullanıcı var mı?
    target = db.query(User).filter(User.id == user_id).first()
    if not target:
        raise HTTPException(404, "Böyle bir kullanıcı yok.")

    # Zaten takip ediliyor mu?
    exists = db.query(Follow).filter(
        Follow.follower_id == current_user.id,
        Follow.following_id == user_id
    ).first()
    if exists:
        raise HTTPException(400, "Zaten takip ediyorsunuz.")

    new_follow = Follow(
        follower_id=current_user.id,
        following_id=user_id
    )
    db.add(new_follow)
    db.commit()

    return {"message": "Takip edildi."}

# ---- Takipten Çık ---- #
@router.delete("/{user_id}")
def unfollow_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    follow = db.query(Follow).filter(
        Follow.follower_id == current_user.id,
        Follow.following_id == user_id
    ).first()

    if not follow:
        raise HTTPException(400, "Zaten takip etmiyorsunuz.")

    db.delete(follow)
    db.commit()

    return {"message": "Takipten çıkıldı."}