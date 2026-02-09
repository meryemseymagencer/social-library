from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .database import get_db
from .models import Rating, Item, Activity, ActivityType
from .security import get_current_user
from .security import get_optional_user

from .schemas import RatingCreate, RatingSummary
router = APIRouter(prefix="/rating", tags=["Rating"])
# RATE OR UPDATE RATING
@router.post("/{item_id}")
def rate_item(
    item_id: int,
    rating_data: RatingCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    # Item var mı?
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        raise HTTPException(404, "Item not found")

    # Önceden rating var mı?
    existing = (
        db.query(Rating)
        .filter(Rating.item_id == item_id, Rating.user_id == current_user.id)
        .first()
    )

    if existing:
        existing.score = rating_data.score
        db.commit()
        db.refresh(existing)

        # Activity güncelle
        activity = Activity(
            user_id=current_user.id,
            item_id=item_id,
            activity_type=ActivityType.rating,
            rating_value=rating_data.score
        )
        db.add(activity)
        db.commit()

        return {"message": "Rating updated", "score": existing.score}

    # Yeni rating
    new_rating = Rating(
        user_id=current_user.id,
        item_id=item_id,
        score=rating_data.score
    )
    db.add(new_rating)
    db.commit()
    db.refresh(new_rating)

    # Activity log
    activity = Activity(
        user_id=current_user.id,
        item_id=item_id,
        activity_type=ActivityType.rating,
        rating_value=rating_data.score
    )
    db.add(activity)
    db.commit()

    return {"message": "Rating added", "score": new_rating.score}
# GET ITEM RATING SUMMARY
@router.get("/{item_id}/summary", response_model=RatingSummary)
def get_item_rating_summary(
    item_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_optional_user)
):
    ratings = db.query(Rating).filter(Rating.item_id == item_id).all()

    if len(ratings) == 0:
        return RatingSummary(average=None, count=0, user_score=None)

    avg = sum(r.score for r in ratings) / len(ratings)

    # user_score sadece kullanıcı giriş yaptıysa hesaplanacak
    user_rating = None
    if current_user:
        user_rating = next((r.score for r in ratings if r.user_id == current_user.id), None)

    return RatingSummary(
        average=round(avg, 2),
        count=len(ratings),
        user_score=user_rating
    )

# GET USER RATINGS
@router.get("/user/{user_id}")
def get_user_ratings(user_id: int, db: Session = Depends(get_db)):
    ratings = (
        db.query(Rating)
        .filter(Rating.user_id == user_id)
        .all()
    )
    return ratings