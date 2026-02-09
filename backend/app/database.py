from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
# BURAYI DAHA SONRA GERÇEK ONLINE POSTGRES URL'İNLE DEĞİŞTİRECEKSİN
# ÖRNEK FORMAT:
# postgresql+psycopg2://kullanici:parola@host:port/veritabani_adi
DATABASE_URL = "postgresql+psycopg2://neondb_owner:npg_9yCx4TXQoJgp@ep-wild-bird-agyjdz02.c-2.eu-central-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"
# DB dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
engine = create_engine(
    DATABASE_URL,
    future=True,
)
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)
Base = declarative_base()
