from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Float
from sqlalchemy.orm import relationship

from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(String)

    balance = relationship("Balance", back_populates="owner")
    transactions = relationship("Transaction", back_populates="owner")

class Balance(Base):
    __tablename__ = "balance"

    id = Column(Integer, primary_key=True)

    user_id = Column(Integer, ForeignKey("users.id"))
    currency_name = Column(String)
    amount = Column(Float)

    owner = relationship("User", back_populates="balance")

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    from_currency = Column(String)
    to_currency = Column(String)
    amount = Column(Float)
    rate = Column(Float)

    owner = relationship("User", back_populates="transactions")
