from sqlalchemy import ( Column, Integer, String, DateTime, Text, ForeignKey, UniqueConstraint, Enum )
from sqlalchemy.orm import relationship
from .database import Base
from datetime import datetime, timezone
import enum
# USER
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    avatar_url = Column(String(500), nullable=True)
    bio = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc),
                        onupdate=lambda: datetime.now(timezone.utc))
    
    # ŞİFRE SIFIRLAMA ALANLARI
    reset_code = Column(String(10), nullable=True)
    reset_code_expires = Column(DateTime, nullable=True)
    # Relationships
    ratings = relationship("Rating", back_populates="user", cascade="all,delete")
    reviews = relationship("Review", back_populates="user", cascade="all,delete")
    lists = relationship("UserList", back_populates="user", cascade="all,delete")
    activities = relationship("Activity", back_populates="user", cascade="all,delete")
   
    # FOLLOW RELATIONSHIPS
    followers = relationship(
        "Follow",
        foreign_keys="Follow.following_id",
        backref="followed_user",
        cascade="all,delete"
    )

    following = relationship(
        "Follow",
        foreign_keys="Follow.follower_id",
        backref="follower_user",
        cascade="all,delete"
    )

# ITEMS (BOOKS / MOVIES)
class ItemType(str, enum.Enum):
    book = "book"
    movie = "movie"
class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True)
    external_id = Column(String(100), unique=True, index=True)  # TMDb ID / Google Books ID
    item_type = Column(Enum(ItemType), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    year = Column(Integer, nullable=True)
    poster_url = Column(String(500), nullable=True)
    authors = Column(Text, nullable=True)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    ratings = relationship("Rating", back_populates="item", cascade="all,delete")
    reviews = relationship("Review", back_populates="item", cascade="all,delete")
# RATINGS
class Rating(Base):
    __tablename__ = "ratings"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    item_id = Column(Integer, ForeignKey("items.id"))
    score = Column(Integer, nullable=False)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc),
                        onupdate=lambda: datetime.now(timezone.utc))

    # Constraints
    __table_args__ = (UniqueConstraint("user_id", "item_id"),)

    user = relationship("User", back_populates="ratings")
    item = relationship("Item", back_populates="ratings")
# REVIEWS
class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    item_id = Column(Integer, ForeignKey("items.id"))
    content = Column(Text, nullable=False)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc),
                        onupdate=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="reviews")
    item = relationship("Item", back_populates="reviews")
class Follow(Base):
    __tablename__ = "follows"

    id = Column(Integer, primary_key=True)
    follower_id = Column(Integer, ForeignKey("users.id"))
    following_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    __table_args__ = (UniqueConstraint("follower_id", "following_id"),)
# USER LISTS
class UserList(Base):
    __tablename__ = "lists"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)

    # Sistem tarafından oluşturulmuş liste mi?
    is_system = Column(Integer, default=0)  # 0 = normal, 1 = sistem listesi

    user = relationship("User", back_populates="lists")
    items = relationship("ListItem", back_populates="list", cascade="all,delete")

class ListItem(Base):
    __tablename__ = "list_items"

    id = Column(Integer, primary_key=True)
    list_id = Column(Integer, ForeignKey("lists.id"))
    item_id = Column(Integer, ForeignKey("items.id"))
    added_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    __table_args__ = (UniqueConstraint("list_id", "item_id"),)

    list = relationship("UserList", back_populates="items")
    item = relationship("Item", backref="list_links")

# ACTIVITY FEED
class ActivityType(str, enum.Enum):
    rating = "rating"
    review = "review"
    list_add = "list_add"
class Activity(Base):
    __tablename__ = "activities"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    item_id = Column(Integer, ForeignKey("items.id"), nullable=True)
    activity_type = Column(Enum(ActivityType))

    rating_value = Column(Integer, nullable=True)
    review_excerpt = Column(Text, nullable=True)
    likes = relationship("ActivityLike", back_populates="activity", cascade="all,delete")
    comments = relationship("ActivityComment", back_populates="activity", cascade="all,delete")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="activities")
class ActivityLike(Base):
    __tablename__ = "activity_likes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    activity_id = Column(Integer, ForeignKey("activities.id", ondelete="CASCADE"))
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    user = relationship("User")
    activity = relationship("Activity", back_populates="likes")
class ActivityComment(Base):
    __tablename__ = "activity_comments"

    id = Column(Integer, primary_key=True, index=True)
    activity_id = Column(Integer, ForeignKey("activities.id", ondelete="CASCADE"))
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    user = relationship("User")
    activity = relationship("Activity", back_populates="comments")
