from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.middleware.cors import CORSMiddleware

from web3_layer import verify_metamask_message_signature
from service import get_all_lootboxes, open_lootbox, get_or_create_user, get_all_prizes, create_prize, create_lootbox
from db import get_async_session
from models import User
from schemas import AuthRequest, AuthResponse, LootboxReadSchema, LootboxOpenSchema, PrizeReadSchema, UserReadSchema, \
    PrizeCreateSchema, LootboxCreateSchema
from users import get_current_user, create_jwt, get_admin_user
from db import create_db_and_tables


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_db_and_tables()
    yield


app = FastAPI(lifespan=lifespan)


origins = [
    "http://localhost:8000",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/auth/verify", response_model=AuthResponse, tags=['users'])
async def verify_signature(data: AuthRequest, s: AsyncSession = Depends(get_async_session)):
    address = verify_metamask_message_signature(data.signature)
    await get_or_create_user(s, address)
    token = create_jwt(address)
    return {"access_token": token, "token_type": "bearer"}


@app.get('/users/me', response_model=UserReadSchema, tags=['users'])
async def get_users_me(user: User = Depends(get_current_user)):
    return user


@app.get('/prizes', response_model=list[PrizeReadSchema], tags=['prizes'])
async def get_prizes_list(user: User = Depends(get_admin_user), s: AsyncSession = Depends(get_async_session)):
    return await get_all_prizes(s)


@app.post('/prizes', response_model=PrizeReadSchema, tags=['prizes'])
async def post_create_prize(
        schema: PrizeCreateSchema,
        user: User = Depends(get_admin_user),
        s: AsyncSession = Depends(get_async_session)
):
    return await create_prize(s, schema)


@app.get('/lootboxes', response_model=list[LootboxReadSchema], tags=['lootboxes'])
async def get_lootboxes_list(s: AsyncSession = Depends(get_async_session)):
    return await get_all_lootboxes(s)


@app.post('/lootboxes', response_model=LootboxReadSchema, tags=['lootboxes'])
async def post_create_lootbox(
        schema: LootboxCreateSchema,
        user: User = Depends(get_admin_user),
        s: AsyncSession = Depends(get_async_session)
):
    return await create_lootbox(s, schema)


@app.post('/lootboxes/open', response_model=PrizeReadSchema, tags=['lootboxes'])
async def post_open_lootbox(
        schema: LootboxOpenSchema,
        user: User = Depends(get_current_user),
        s: AsyncSession = Depends(get_async_session)
):
    return await open_lootbox(schema, user, s)