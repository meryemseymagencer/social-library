from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc
from .database import get_db
from .security import get_current_user
from .models import Review, Item, Activity, ActivityType
from .schemas import ReviewCreate, ReviewResponse

router = APIRouter(prefix="/reviews", tags=["Reviews"])
# 1) YORUM OLUŞTUR
@router.post("/{item_id}", response_model=ReviewResponse)
def create_review(
    item_id: int,
    review_data: ReviewCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        raise HTTPException(404, "Item not found")

    review = Review(
        user_id=current_user.id,
        item_id=item_id,
        content=review_data.content
    )
    db.add(review)
    db.commit()
    db.refresh(review)

    # Activity kaydı
    activity = Activity(
        user_id=current_user.id,
        item_id=item_id,
        activity_type=ActivityType.review,
        review_excerpt=review.content[:120]  # önizleme
    )
    db.add(activity)
    db.commit()

    return review
# 2) YORUM GÜNCELLE
@router.put("/{review_id}", response_model=ReviewResponse)
def update_review(
    review_id: int,
    review_data: ReviewCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    review = db.query(Review).filter(Review.id == review_id).first()
    if not review:
        raise HTTPException(404, "Review not found")

    if review.user_id != current_user.id:
        raise HTTPException(403, "Bu yorumu güncelleme yetkin yok")

    review.content = review_data.content
    db.commit()
    db.refresh(review)

    # Activity kaydı
    activity = Activity(
        user_id=current_user.id,
        item_id=review.item_id,
        activity_type=ActivityType.review,
        review_excerpt=review.content[:120]
    )
    db.add(activity)
    db.commit()

    return review
# 3) YORUM SİL
@router.delete("/{review_id}")
def delete_review(
    review_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    review = db.query(Review).filter(Review.id == review_id).first()
    if not review:
        raise HTTPException(404, "Review not found")

    if review.user_id != current_user.id:
        raise HTTPException(403, "Bu yorumu silme yetkin yok")

    db.delete(review)
    db.commit()

    return {"message": "Review deleted"}
# 4) ITEM'A AİT TÜM YORUMLAR
from .models import Review, User

@router.get("/item/{item_id}")
def get_item_reviews(item_id: int, db: Session = Depends(get_db)):
    rows = (
        db.query(Review, User)
        .join(User, Review.user_id == User.id)
        .filter(Review.item_id == item_id)
        .order_by(desc(Review.created_at))
        .all()
    )

    result = []
    for r, u in rows:
        result.append({
            "id": r.id,
            "content": r.content,
            "created_at": r.created_at,
            "user": {
                "id": u.id,
                "username": u.username,
                "avatar_url": getattr(u, "avatar_url", None)
            }
        })

    return result

# 5) KULLANICININ YORUMLARI
@router.get("/user/{user_id}", response_model=list[ReviewResponse])
def get_user_reviews(user_id: int, db: Session = Depends(get_db)):
    reviews = (
        db.query(Review)
        .filter(Review.user_id == user_id)
        .order_by(desc(Review.created_at))
        .all()
    )
    return reviews