import uuid
from datetime import datetime
from decimal import Decimal
from typing import Literal
from pydantic import BaseModel, Field
from config import PrizeQualityEnum, PrizeTypeEnum, PLATFORM_URL


class TonPayload(BaseModel):
    payload: str


class Domain(BaseModel):
    lengthBytes: int = len(PLATFORM_URL)
    value: str = PLATFORM_URL


class TonProof(BaseModel):
    timestamp: int
    domain: Domain
    signature: str
    payload: str


class TonProofItem(BaseModel):
    name: Literal['ton_proof'] = 'ton_proof'
    address: str
    public_key: str = Field(alias='publicKey')
    proof: TonProof


class AuthResponse(BaseModel):
    access_token: str = Field(serialization_alias='accessToken')
    token_type: str = Field(serialization_alias='tokenType')


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
    tokens_amount: Decimal


class PrizeCreateSchema(BaseModel):
    name: str
    lootbox_id: int
    quality: PrizeQualityEnum
    drop_chance: Decimal
    type: PrizeTypeEnum
    tokens_amount: Decimal


class ClaimedPrizeReadSchema(BaseModel):
    id: int
    claim_date: datetime
    prize: PrizeReadSchema


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
