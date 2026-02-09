from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc
from .database import get_db
from .models import Activity, Follow, User, Item, ActivityLike
from .security import get_current_user
from .models import ActivityComment

router = APIRouter(prefix="/activity", tags=["Activity"])


# ⭐ LIKE
@router.post("/{activity_id}/like")
def like_activity(
    activity_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    act = db.query(Activity).filter(Activity.id == activity_id).first()
    if not act:
        raise HTTPException(status_code=404, detail="Activity not found")

    existing = db.query(ActivityLike).filter_by(
        user_id=current_user.id,
        activity_id=activity_id
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="Already liked")

    new_like = ActivityLike(
        user_id=current_user.id,
        activity_id=activity_id
    )

    db.add(new_like)
    db.commit()
    return {"status": "liked"}


# ⭐ UNLIKE
@router.delete("/{activity_id}/like")
def unlike_activity(
    activity_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    deleted = db.query(ActivityLike).filter_by(
        user_id=current_user.id,
        activity_id=activity_id
    ).delete()

    db.commit()

    if not deleted:
        raise HTTPException(status_code=400, detail="Not liked")

    return {"status": "unliked"}


#  FEED
@router.get("/feed")
def get_feed(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    following_ids = (
        db.query(Follow.following_id)
        .filter(Follow.follower_id == current_user.id)
        .all()
    )

    following_ids = [f[0] for f in following_ids]

    if not following_ids:
        return []

    activities = (
        db.query(Activity, User, Item)
        .join(User, Activity.user_id == User.id)
        .join(Item, Activity.item_id == Item.id)
        .filter(Activity.user_id.in_(following_ids))
        .order_by(desc(Activity.created_at))
        .limit(50)
        .all()
    )

    result = []

    for activity, user, item in activities:

        like_count = db.query(ActivityLike).filter(
            ActivityLike.activity_id == activity.id
        ).count()

        is_liked_by_me = (
            db.query(ActivityLike)
            .filter(
                ActivityLike.activity_id == activity.id,
                ActivityLike.user_id == current_user.id
            )
            .first()
            is not None
        )
        comment_count = db.query(ActivityComment).filter(
                ActivityComment.activity_id == activity.id
            ).count()
        result.append({
            "id": activity.id,
            "activity_type": activity.activity_type,
            "created_at": activity.created_at,

            "comment_count": comment_count,    # ← BURAYA VİRGÜL EKLENDİ

            "user": {
                "id": user.id,
                "username": user.username,
                "avatar_url": user.avatar_url
            },

            "item": {
                "id": item.id,
                "title": item.title,
                "poster_url": item.poster_url
            },

            "rating_value": activity.rating_value,
            "review_excerpt": activity.review_excerpt,

            "like_count": like_count,
            "is_liked_by_me": is_liked_by_me
        })

    return result
@router.post("/{activity_id}/comment")
def add_comment(
    activity_id: int,
    content: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    act = db.query(Activity).filter(Activity.id == activity_id).first()
    if not act:
        raise HTTPException(status_code=404, detail="Activity not found")

    comment = ActivityComment(
        activity_id=activity_id,
        user_id=current_user.id,
        content=content
    )

    db.add(comment)
    db.commit()
    db.refresh(comment)

    return {
        "id": comment.id,
        "content": comment.content,
        "created_at": comment.created_at,
        "user": {
            "id": current_user.id,
            "username": current_user.username,
            "avatar_url": current_user.avatar_url
        }
    }

@router.get("/{activity_id}/comments")
def get_comments(
    activity_id: int,
    db: Session = Depends(get_db)
):
    comments = (
        db.query(ActivityComment, User)
        .join(User, ActivityComment.user_id == User.id)
        .filter(ActivityComment.activity_id == activity_id)
        .order_by(ActivityComment.created_at.asc())
        .all()
    )

    result = []
    for comment, user in comments:
        result.append({
            "id": comment.id,
            "content": comment.content,
            "created_at": comment.created_at,
            "user": {
                "id": user.id,
                "username": user.username,
                "avatar_url": user.avatar_url
            }
        })

    return result

@router.delete("/comment/{comment_id}")
def delete_comment(
    comment_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    comment = db.query(ActivityComment).filter(ActivityComment.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")

    if comment.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="You cannot delete this comment")

    db.delete(comment)
    db.commit()

    return {"status": "deleted"}
