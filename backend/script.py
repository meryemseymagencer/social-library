from app.database import SessionLocal
from app import models

db = SessionLocal()

default_lists = [
    ("Okudum", "Okuduğun kitaplar"),
    ("Okuyacağım", "Okumayı düşündüğün kitaplar"),
    ("İzledim", "İzlediğin filmler"),
    ("İzleyeceğim", "İzlemeyi düşündüğün filmler"),
]

users = db.query(models.User).all()

for user in users:
    existing = db.query(models.UserList).filter(models.UserList.user_id == user.id).count()

    if existing >= 4:
        continue  # zaten var

    for name, desc in default_lists:
        lst = models.UserList(
            user_id=user.id,
            name=name,
            description=desc
        )
        db.add(lst)

db.commit()
