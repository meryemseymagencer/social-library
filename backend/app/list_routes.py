from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc
from .database import get_db
from .security import get_current_user
from .models import UserList, ListItem, Item, Activity, ActivityType
from .schemas import ListCreate, ListUpdate, ListResponse, ItemSummary
router = APIRouter(prefix="/lists", tags=["Lists"])
print("🔥 list_routes YÜKLENDİ")
from .security import get_optional_user
# --- 1) GET MY LISTS  ---
@router.get("/me", response_model=list[ListResponse])
def get_my_lists(
    db: Session = Depends(get_db),
    current_user = Depends(get_optional_user)
):
    print("🔥 /lists/me ÇALIŞTI | current_user =", current_user)
    if not current_user:
        return []

    # 1) Varsayılan listeler yoksa otomatik oluştur
    create_default_lists(db, current_user.id)

    # 2) Tüm listeleri döndür
    lists = db.query(UserList).filter_by(user_id=current_user.id).all()

    response = []
    for lst in lists:
        items = []
        for li in lst.items:
            if not li.item:
                continue

            items.append(
                ItemSummary(
                    id=li.item.id,
                    title=li.item.title,
                    year=li.item.year,
                    poster_url=li.item.poster_url
                )
            )


        response.append(
            ListResponse(
                id=lst.id,
                user_id=lst.user_id,
                name=lst.name,
                description=lst.description,
                is_system=lst.is_system,
                item_count=len(items),
                items=items
            )
        )

    return response

# CREATE LIST
@router.post("", response_model=ListResponse)
def create_list(
    list_data: ListCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    new_list = UserList(
        user_id=current_user.id,
        name=list_data.name,
        description=list_data.description
    )
    db.add(new_list)
    db.commit()
    db.refresh(new_list)

    # yeni liste boş olduğu için
    return ListResponse(
        id=new_list.id,
        user_id=new_list.user_id,
        name=new_list.name,
        description=new_list.description,
        is_system=new_list.is_system,
        item_count=0,
        items=[]
    )

# GET LIST DETAILS
@router.get("/{list_id}", response_model=ListResponse)
def get_list(list_id: int, db: Session = Depends(get_db)):
    lst = db.query(UserList).filter(UserList.id == list_id).first()
    if not lst:
        raise HTTPException(404, "List not found")

    items = [
        ItemSummary(
            id=i.item.id,
            title=i.item.title,
            year=i.item.year,
            poster_url=i.item.poster_url
        )
        for i in lst.items
    ]

    return ListResponse(
        id=lst.id,
        user_id=lst.user_id,
        name=lst.name,
        description=lst.description,
        is_system=lst.is_system,
        item_count=len(items),
        items=items
    )

# GET USER LISTS
@router.get("/user/{user_id}", response_model=list[ListResponse])
def get_user_lists(user_id: int, db: Session = Depends(get_db)):
    lists = db.query(UserList).filter(UserList.user_id == user_id).all()

    response = []
    for lst in lists:
        items = [
            ItemSummary(
                id=li.item.id,
                title=li.item.title,
                year=li.item.year,
                poster_url=li.item.poster_url
            )
            for li in lst.items
        ]

        response.append(
            ListResponse(
                id=lst.id,
                user_id=lst.user_id,
                name=lst.name,
                description=lst.description,
                is_system=lst.is_system,
                item_count=len(items),
                items=items
            )
        )

    return response

# UPDATE LIST
@router.put("/{list_id}", response_model=ListResponse)
def update_list(
    list_id: int,
    list_data: ListUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    lst = db.query(UserList).filter(UserList.id == list_id).first()
    if not lst:
        raise HTTPException(404, "List not found")

    if lst.user_id != current_user.id:
        raise HTTPException(403, "Unauthorized")

    # SYSTEM LIST DÜZENLENEMEZ
    if lst.is_system == 1:
        raise HTTPException(403, "System lists cannot be edited")

    if list_data.name is not None:
        lst.name = list_data.name

    if list_data.description is not None:
        lst.description = list_data.description

    db.commit()
    db.refresh(lst)

# DELETE LIST
@router.delete("/{list_id}")
def delete_list(
    list_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    lst = db.query(UserList).filter(UserList.id == list_id).first()
    if not lst:
        raise HTTPException(404, "List not found")

    if lst.user_id != current_user.id:
        raise HTTPException(403, "Unable to delete other user's list")

    # SYSTEM LIST SİLİNEMEZ
    if lst.is_system == 1:
        raise HTTPException(403, "System lists cannot be deleted")

    db.delete(lst)
    db.commit()

    return {"message": "List deleted"}


# ADD ITEM TO LIST
@router.post("/{list_id}/items/{item_id}")
def add_item_to_list(
    list_id: int,
    item_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    lst = db.query(UserList).filter(UserList.id == list_id).first()
    if not lst:
        raise HTTPException(404, "List not found")

    if lst.user_id != current_user.id:
        raise HTTPException(403, "Unauthorized")

    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        raise HTTPException(404, "Item not found")

    exists = (
        db.query(ListItem)
        .filter(ListItem.list_id == list_id, ListItem.item_id == item_id)
        .first()
    )
    if exists:
        return {"message": "Already in list"}

    li = ListItem(list_id=list_id, item_id=item_id)
    db.add(li)
    db.commit()

    return {"message": "Item added"}

# REMOVE ITEM
@router.delete("/{list_id}/items/{item_id}")
def remove_item_from_list(
    list_id: int,
    item_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    lst = db.query(UserList).filter(UserList.id == list_id).first()
    if not lst:
        raise HTTPException(404, "List not found")

    if lst.user_id != current_user.id:
        raise HTTPException(403, "Unauthorized")

    entry = (
        db.query(ListItem)
        .filter(ListItem.list_id == list_id, ListItem.item_id == item_id)
        .first()
    )
    if not entry:
        raise HTTPException(404, "Item not in list")

    db.delete(entry)
    db.commit()

    return {"message": "Item removed from list"}

from .security import get_optional_user


# CREATE MY LIST
@router.post("/me", response_model=ListResponse)
def create_my_list(
    list_data: ListCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    new_list = UserList(
        user_id=current_user.id,
        name=list_data.name,
        description=list_data.description
    )
    db.add(new_list)
    db.commit()
    db.refresh(new_list)

    return ListResponse(
        id=new_list.id,
        user_id=new_list.user_id,
        name=new_list.name,
        description=new_list.description,
        is_system=new_list.is_system,
        item_count=0,
        items=[]
    )
def create_default_lists(db, user_id):
    default_lists = [
        ("Okudum", "Okuduğun kitaplar"),
        ("Okuyacağım", "Okumayı düşündüğün kitaplar"),
        ("İzledim", "İzlediğin filmler"),
        ("İzleyeceğim", "İzlemeyi düşündüğün filmler"),
    ]

    created = []

    for name, desc in default_lists:
        exists = db.query(UserList).filter_by(
            user_id=user_id,
            name=name
        ).first()

        if not exists:
            new_list = UserList(
                user_id=user_id,
                name=name,
                description=desc,
                is_system=1    
            )
            db.add(new_list)
            created.append(new_list)

    db.commit()
    return created

@router.get("/default/{name}")
def get_default_list(name: str, db: Session = Depends(get_db), current_user=Depends(get_current_user)):

    lst = db.query(UserList).filter_by(
        user_id=current_user.id,
        name=name,
        is_system=1
    ).first()

    if not lst:
        raise HTTPException(404, "Default list not found")

    return {"id": lst.id}
