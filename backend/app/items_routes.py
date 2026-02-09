# app/items_routes.py
import httpx
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .database import get_db
from .models import Item, ItemType
from datetime import datetime

router = APIRouter(prefix="/items", tags=["Items"])
from dotenv import load_dotenv
import os

load_dotenv()

TMDB_API_KEY = os.getenv("TMDB_API_KEY")

TMDB_BASE_URL = "https://api.themoviedb.org/3"
# ----------------------------
# GET POPULAR MOVIES
# ----------------------------
@router.get("/popular/movies")
async def get_popular_movies(db: Session = Depends(get_db)):
    url = f"{TMDB_BASE_URL}/movie/popular?api_key={TMDB_API_KEY}&language=en-US"

    async with httpx.AsyncClient() as client:
        resp = await client.get(url)

    if resp.status_code != 200:
        raise HTTPException(500, "TMDb bağlantı hatası")

    data = resp.json()["results"][:20]  # İlk 20 film

    popular_items = []
    for m in data:
        poster = (
            f"https://image.tmdb.org/t/p/w500{m['poster_path']}"
            if m.get("poster_path")
            else None
        )

        external_id = f"tmdb_{m['id']}"

        # DB'de var mı kontrol et
        item = db.query(Item).filter(Item.external_id == external_id).first()

        if not item:
            # Yeni kayıt
            item = Item(
                external_id=external_id,
                item_type=ItemType.movie,
                title=m["title"],
                description=m.get("overview"),
                year=int(m["release_date"][:4]) if m.get("release_date") else None,
                poster_url=poster,
                created_at=datetime.utcnow(),
            )
            db.add(item)
            db.commit()
            db.refresh(item)

        popular_items.append(item)

    return popular_items
# ----------------------------
# GET POPULAR BOOKS
# ----------------------------
@router.get("/popular/books")
async def get_popular_books(db: Session = Depends(get_db)):
    url = (
        "https://www.googleapis.com/books/v1/volumes?"
        "q=subject:fiction&maxResults=20&orderBy=relevance"
    )

    async with httpx.AsyncClient() as client:
        resp = await client.get(url)

    if resp.status_code != 200:
        raise HTTPException(500, "Google Books bağlantı hatası")

    data = resp.json().get("items", [])

    popular_items = []

    for b in data:
        info = b["volumeInfo"]
        external_id = f"gbook_{b['id']}"

        # Poster
        poster = info.get("imageLinks", {}).get("thumbnail")

        # DB'de var mı?
        item = db.query(Item).filter(Item.external_id == external_id).first()

        if not item:
            item = Item(
                external_id=external_id,
                item_type=ItemType.book,
                title=info.get("title"),
                description=info.get("description"),
                year=info.get("publishedDate", "")[:4] if info.get("publishedDate") else None,
                authors=", ".join(info.get("authors", [])),
                poster_url=poster,
                created_at=datetime.utcnow(),
            )
            db.add(item)
            db.commit()
            db.refresh(item)

        popular_items.append(item)

    return popular_items
# ----------------------------
# FILTER ITEMS
# ----------------------------
from sqlalchemy import func

@router.get("/filter")
def filter_items(
    item_type: str | None = None,
    year: int | None = None,
    genre: str | None = None,
    min_rating: float | None = None,
    db: Session = Depends(get_db)
):
    query = db.query(Item)

    if item_type:
        query = query.filter(Item.item_type == item_type)

    if year:
        query = query.filter(Item.year == year)

    if genre:
        query = query.filter(Item.genres.ilike(f"%{genre}%"))  # genres TEXT alanında

    items = query.all()

    # Rating filtresi gerekiyorsa hesapla
    if min_rating:
        filtered = []
        for item in items:
            if len(item.ratings) == 0:
                continue
            avg_score = sum(r.score for r in item.ratings) / len(item.ratings)
            if avg_score >= min_rating:
                filtered.append(item)
        return filtered

    return items
# ----------------------------
# GET SINGLE ITEM BY ID
# ----------------------------
@router.get("/{item_id}")
def get_item(item_id: int, db: Session = Depends(get_db)):
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        raise HTTPException(404, "Item not found")
    return item
