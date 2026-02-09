from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from . import models
from .database import engine

print("🔥🔥🔥 FASTAPI MAIN.PY YÜKLENDİ 🔥🔥🔥")

# ---------------------------------------------------------
# 1) APP OLUŞTURMA
# ---------------------------------------------------------
app = FastAPI()

# ---------------------------------------------------------
# 2) CORS → Router'lardan ÖNCE GELMELİ !!!
# ---------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "*",   # ← TEST AMAÇLI TAM SERBEST BIRAK
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------
# 3) DATABASE MODELS OLUŞTUR
# ---------------------------------------------------------
models.Base.metadata.create_all(bind=engine)

# ---------------------------------------------------------
# 4) ROUTER'LAR (SIRASI ÖNEMLİ DEĞİL AMA CORS'TAN SONRA OLMALI)
# ---------------------------------------------------------
from .auth_routes import router as auth_router
app.include_router(auth_router, prefix="/auth", tags=["Auth"])

from .users_routes import router as user_router
app.include_router(user_router, tags=["Users"])

from .follow_routes import router as follow_router
app.include_router(follow_router)

from .items_routes import router as items_router
app.include_router(items_router)

from .rating_routes import router as rating_router
app.include_router(rating_router)

from .activity_routes import router as activity_router
app.include_router(activity_router)

from .review_routes import router as review_router
app.include_router(review_router)

from .list_routes import router as list_router
app.include_router(list_router)

# ---------------------------------------------------------
# 5) STATIC (HER ZAMAN EN SON)
# ---------------------------------------------------------
app.mount("/static", StaticFiles(directory="static"), name="static")
