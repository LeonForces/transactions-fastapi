from sqlalchemy.orm import Session
from sqlalchemy.sql import func

from . import models, schemas


def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.Transaction.id == user_id).first()


def get_user_by_name(db: Session, name: str):
    return db.query(models.User).filter(models.User.name == name).first()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()


def get_transaction(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Transaction).offset(skip).limit(limit).all()


def create_user(db: Session, user: schemas.UserCreate):
    db_user = models.User(name=user.name, balance=user.balance)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def create_user_transaction(db: Session, item: schemas.TransactionCreate):
    db_item = models.Transaction(from_user_id=item.from_user_id, to_user_id=item.to_user_id, amount=item.amount)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


def get_user_transaction(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.Transaction).filter(models.Transaction.from_user_id == user_id).offset(skip).limit(limit).all()


def get_user_debit(db: Session, user_id: int):
    return db.query(func.sum(models.Transaction.amount)).filter(models.Transaction.to_user_id == user_id).scalar()


def get_user_credit(db: Session, user_id: int):
    return db.query(func.sum(models.Transaction.amount)).filter(models.Transaction.from_user_id == user_id).scalar()

