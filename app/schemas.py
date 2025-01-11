import uuid
from decimal import Decimal

from pydantic import BaseModel


class AuthRequest(BaseModel):
    signature: str


class AuthResponse(BaseModel):
    access_token: str
    token_type: str


class UserReadSchema(BaseModel):
    id: uuid.UUID
    address: str
    name: str | None
    balance: Decimal


class PrizeReadSchema(BaseModel):
    id: int
    name: str


class PrizeCreateSchema(BaseModel):
    name: str
    lootbox_id: int


class LootboxReadSchema(BaseModel):
    id: int
    name: str
    prizes: list[PrizeReadSchema]


class LootboxCreateSchema(BaseModel):
    name: str


class LootboxOpenSchema(BaseModel):
    id: int
