from pydantic import BaseModel


class TransactionBase(BaseModel):
    from_user_id: int
    to_user_id: int
    amount: int


class TransactionCreate(TransactionBase):
    pass


class Transaction(TransactionBase):

    class Config:
        orm_mode = True


class UserBase(BaseModel):
    name: str
    balance: int


class UserCreate(UserBase):
    pass


class User(UserBase):
    id: int
    items: list[Transaction] = []

    class Config:
        orm_mode = True
