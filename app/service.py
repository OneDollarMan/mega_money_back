import random
from typing import Sequence
from fastapi import HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from starlette import status
from config import CHUNK_SIZE, STATIC_PATH, PLATFORM_URL
from schemas import LootboxOpenSchema, PrizeCreateSchema, LootboxCreateSchema
from models import User, Lootbox, Prize
import aiofiles


def get_file_path(lootbox_id: int):
    return f"{STATIC_PATH}/{lootbox_id}.png"


async def get_user_by_address(s: AsyncSession, address: str) -> User | None:
    user = await s.execute(select(User).filter(User.address == address))
    user = user.scalar()
    return user


async def get_or_create_user(s: AsyncSession, address: str) -> User:
    user = await get_user_by_address(s, address)
    if not user:
        user = User(address=address, name=None)
        s.add(user)
        await s.commit()
        await s.refresh(user)
    return user


async def get_all_prizes(s: AsyncSession) -> Sequence[Prize]:
    prizes = await s.execute(select(Prize))
    return prizes.scalars().all()


async def create_prize(s: AsyncSession, schema: PrizeCreateSchema) -> Prize:
    lootbox = await get_lootbox_by_id(s, schema.lootbox_id)
    if not lootbox:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lootbox not found")
    prize = Prize(
        name=schema.name,
        lootbox_id=lootbox.id,
        quality=schema.quality.value,
        drop_chance=schema.drop_chance,
        type=schema.type.value
    )
    s.add(prize)
    await s.commit()
    await s.refresh(prize)
    return prize


async def get_all_lootboxes(s: AsyncSession) -> Sequence[Lootbox]:
    lootboxes = await s.execute(select(Lootbox).options(selectinload(Lootbox.prizes)))
    return lootboxes.scalars().all()


async def get_lootbox_by_id(s: AsyncSession, lootbox_id: int) -> Lootbox | None:
    lootbox = await s.execute(
        select(Lootbox).filter(Lootbox.id == lootbox_id).options(selectinload(Lootbox.prizes)).limit(1)
    )
    return lootbox.scalar()


async def create_lootbox(s: AsyncSession, schema: LootboxCreateSchema) -> Lootbox:
    lootbox = Lootbox(**schema.model_dump())
    s.add(lootbox)
    await s.commit()
    await s.refresh(lootbox, ['prizes'])
    return lootbox


async def upload_lootbox_image(s: AsyncSession, lootbox_id: int, file: UploadFile) -> Lootbox:
    lootbox = await get_lootbox_by_id(s, lootbox_id)
    if not lootbox:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lootbox not found")
    if file.content_type != 'image/png':
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Image should have PNG type")

    async with aiofiles.open(get_file_path(lootbox_id), mode='wb+') as f:
        while chunk := await file.read(CHUNK_SIZE):
            await f.write(chunk)

    lootbox.image_url = f'{PLATFORM_URL}/static/{lootbox_id}.png'
    await s.commit()
    return lootbox


async def open_lootbox(schema: LootboxOpenSchema, user: User, s: AsyncSession) -> Prize | None:
    lootbox = await get_lootbox_by_id(s, schema.id)
    if not lootbox:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lootbox not found")

    if len(lootbox.prizes) == 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Lootbox has no prizes")

    weights = [float(prize.drop_chance) for prize in lootbox.prizes]
    return random.choices(lootbox.prizes, weights=weights)[0]

