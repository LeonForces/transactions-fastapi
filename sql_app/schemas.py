from pydantic import BaseModel


class TransactionBase(BaseModel):
    from_currency: str
    to_currency: str
    amount: float


class TransactionCreate(TransactionBase):
    pass


class Transaction(TransactionBase):
    rate: float
    user_id: int
    class Config:
        orm_mode = True


class Balance(BaseModel):
    currency_name: str
    amount: float

class UserBase(BaseModel):
    name: str


class UserCreate(UserBase):
    pass


class User(UserBase):
    id: int
    balance: list[Balance]
    transactions: list[Transaction] = []

    class Config:
        orm_mode = True
