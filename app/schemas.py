import uuid
from decimal import Decimal
from pydantic import BaseModel
from config import PrizeQualityEnum, PrizeTypeEnum


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
    lootbox_id: int
    quality: PrizeQualityEnum
    drop_chance: Decimal
    type: PrizeTypeEnum


class PrizeCreateSchema(BaseModel):
    name: str
    lootbox_id: int
    quality: PrizeQualityEnum
    drop_chance: Decimal
    type: PrizeTypeEnum


class LootboxReadSchema(BaseModel):
    id: int
    name: str
    image_url: str | None
    open_price: Decimal
    prizes: list[PrizeReadSchema]


class LootboxCreateSchema(BaseModel):
    name: str
    open_price: Decimal


class LootboxOpenSchema(BaseModel):
    id: int
