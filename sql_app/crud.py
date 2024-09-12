from sqlalchemy.orm import Session

from . import models, schemas

from urllib.request import urlopen
import xml.etree.ElementTree as ET


def get_rate(from_currency: str, to_currency: str):
    with urlopen('https://www.cbr.ru/scripts/XML_daily.asp') as f:
        tree = ET.parse(f)
        root = tree.getroot()
        
    rate_USD, rate_EUR = 0, 0
    for valute in root.iter():
        if valute.get('ID') == "R01235":  # Курс доллара США
            nominal = float(valute.find('Nominal').text.replace(',', '.'))
            rate_USD = float(valute.find('Value').text.replace(',', '.')) / nominal
        if valute.get('ID') == "R01239":  # Курс евро
            nominal = float(valute.find('Nominal').text.replace(',', '.'))
            rate_EUR = float(valute.find('Value').text.replace(',', '.')) / nominal
    
    rate = 0
    match from_currency:
        case "RUB":
            match to_currency:
                case "USD":
                    rate = 1 / rate_USD
                case "EUR":
                    rate = 1 / rate_EUR
        case "USD":
            match to_currency:
                case "RUB":
                    rate = rate_USD
                case "EUR":
                    rate = rate_USD / rate_EUR
        case "EUR":
            match to_currency:
                case "USD":
                    rate = rate_EUR / rate_USD
                case "RUB":
                    rate = rate_EUR
    
    return rate


def create_user(db: Session, user: schemas.UserCreate):
    db_user = models.User(name=user.name)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def create_user_balance(db: Session, balance: schemas.Balance, user_id: int):
    db_balance = models.Balance(user_id=user_id, currency_name=balance.currency_name, amount=balance.amount)
    db.add(db_balance)
    db.commit()
    db.refresh(db_balance)
    return db_balance


def create_user_transaction(db: Session, user_id: int, transaction: schemas.TransactionCreate, rate: float):
    db_item = models.Transaction(user_id=user_id,
                                 from_currency=transaction.from_currency,
                                 to_currency=transaction.to_currency,
                                 amount=transaction.amount,
                                 rate=rate)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_name(db: Session, name: str):
    return db.query(models.User).filter(models.User.name == name).first()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()


def get_user_balance(db: Session, user_id: int, from_currency: str):
    return db.query(models.Balance).filter(models.Balance.currency_name == from_currency and models.Balance.user_id == user_id).first()


def get_transactions(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Transaction).offset(skip).limit(limit).all()


def get_user_transactions(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.Transaction).filter(models.Transaction.user_id == user_id).offset(skip).limit(limit).all()


"""def get_user_debit(db: Session, user_id: int):
    return db.query(func.sum(models.Transaction.amount)).filter(models.Transaction.to_user_id == user_id).scalar()


def get_user_credit(db: Session, user_id: int):
    return db.query(func.sum(models.Transaction.amount)).filter(models.Transaction.from_user_id == user_id).scalar()"""

