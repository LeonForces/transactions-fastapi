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


@app.post("/users/create/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_name(db, name=user.name)
    if db_user:
        raise HTTPException(status_code=400, detail="User has been already registered")
    return crud.create_user(db=db, user=user)


@app.post("/balance/create/{user_id}", response_model=schemas.Balance)
def create_user_balance(user_id: int, balance: schemas.Balance, db: Session = Depends(get_db)):
    balance.currency_name = balance.currency_name.upper()
    if balance.currency_name not in ["RUB", "USD", "EUR"]:
        raise HTTPException(status_code=400, detail="Сan not find this currency")

    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=400, detail="User not found")
    check_balance = crud.get_user_balance(db, user_id=user_id, from_currency=balance.currency_name)
    if check_balance:
        raise HTTPException(status_code=400, detail="Balance has been already added")
    return crud.create_user_balance(db=db, balance=balance, user_id=user_id)


@app.post("/transactions/{user_id}", response_model=schemas.Transaction)
def create_user_transaction(
    user_id: int, transaction: schemas.TransactionCreate, db: Session = Depends(get_db)
):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")

    from_balance = crud.get_user_balance(db, user_id=user_id, from_currency=transaction.from_currency)
    to_balance = crud.get_user_balance(db, user_id=user_id, from_currency=transaction.to_currency)
    if from_balance.currency_name == to_balance.currency_name:
        raise HTTPException(status_code=404, detail="The balances match")
    if from_balance is None or to_balance is None:
        raise HTTPException(status_code=404, detail="User balance not found")
    if from_balance.amount < transaction.amount:
        raise HTTPException(status_code=404, detail="Not enough money")

    rate = crud.get_rate(from_currency=from_balance.currency_name, to_currency=to_balance.currency_name)
    from_balance.amount = models.Balance.amount - transaction.amount
    to_balance.amount = models.Balance.amount + (transaction.amount * rate)

    return crud.create_user_transaction(db=db, user_id=user_id, transaction=transaction, rate=rate)


@app.get("/users/", response_model=list[schemas.User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_users(db, skip=skip, limit=limit)


@app.get("/users/{user_id}", response_model=schemas.User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@app.get("/transactions/", response_model=list[schemas.Transaction])
def read_transactions(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_transactions(db, skip=skip, limit=limit)


@app.get("/transactions/{user_id}", response_model=list[schemas.Transaction])
def read_user_transactions(user_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return crud.get_user_transactions(db, user_id=user_id, skip=skip, limit=limit)


@app.get("/balance/{user_id}", response_model=list[schemas.Balance])
def read_user_balance(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user.balance


@app.get("/invoice/{user_id}/{to_currency}", response_model=int)
def read_user_debit(user_id: int, to_currency: str, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    if to_currency not in ['RUB', 'USD', 'EUR']:
        raise HTTPException(status_code=404, detail="Currency not found")
    debit = crud.get_user_debit(db, user_id=user_id, to_currency=to_currency)
    if debit is None:
        debit = 0
    return debit


@app.get("/withdraw/{user_id}/{from_currency}", response_model=int)
def read_user_credit(user_id: int, from_currency: str, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    if from_currency not in ['RUB', 'USD', 'EUR']:
        raise HTTPException(status_code=404, detail="Currency not found")
    credit = crud.get_user_credit(db, user_id=user_id, from_currency=from_currency)
    if credit is None:
        credit = 0
    return credit

