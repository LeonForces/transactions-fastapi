from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from . import crud, models, schemas
from .database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_name(db, name=user.name)
    if db_user:
        raise HTTPException(status_code=400, detail="User has been already registered")
    return crud.create_user(db=db, user=user)


@app.post("/users/items", response_model=schemas.Transaction)
def create_transaction_for_user(
    item: schemas.TransactionCreate, db: Session = Depends(get_db)
):
    return crud.create_user_transaction(db=db, item=item)


@app.get("/users/", response_model=list[schemas.User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = crud.get_users(db, skip=skip, limit=limit)
    return users


@app.get("/users/{user_id}", response_model=schemas.User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@app.get("/transactions/", response_model=list[schemas.Transaction])
def read_transactions(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    transactions = crud.get_transaction(db, skip=skip, limit=limit)
    return transactions


@app.get("/transactions/{user_id}", response_model=list[schemas.Transaction])
def read_user_transactions(user_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    transactions = crud.get_user_transaction(db, user_id=user_id, skip=skip, limit=limit)
    return transactions


@app.get("/balance/{user_id}", response_model=int)
def read_user_balance(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user.balance


@app.get("/invoice/{user_id}", response_model=int)
def read_user_debit(user_id: int, db: Session = Depends(get_db)):
    debit = crud.get_user_debit(db, user_id=user_id)
    return debit


@app.get("/withdraw/{user_id}", response_model=int)
def read_user_credit(user_id: int, db: Session = Depends(get_db)):
    credit = crud.get_user_credit(db, user_id=user_id)
    return credit
