from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.middleware.cors import CORSMiddleware
from web3_layer import generate_ton_payload, verify_ton_proof
from service import get_all_lootboxes, open_lootbox, get_or_create_user, get_all_prizes, create_prize, create_lootbox, \
    upload_lootbox_image, get_user_claimed_prizes
from db import get_async_session
from models import User
from schemas import TonProofItem, AuthResponse, LootboxReadSchema, LootboxOpenSchema, PrizeReadSchema, UserReadSchema, \
    PrizeCreateSchema, LootboxCreateSchema, ClaimedPrizeReadSchema, TonPayload
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
    "http://127.0.0.1:8000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/auth/payload", response_model=TonPayload, tags=['users'])
async def get_payload():
    return generate_ton_payload()


@app.post("/auth/verify", response_model=AuthResponse, tags=['users'])
async def verify_signature(data: TonProofItem, s: AsyncSession = Depends(get_async_session)):
    address = verify_ton_proof(data)
    await get_or_create_user(s, address)
    token = create_jwt(address)
    return AuthResponse(access_token=token, token_type='bearer')


@app.get('/users/me', response_model=UserReadSchema, tags=['users'])
async def get_user(user: User = Depends(get_current_user)):
    return user


@app.get('/users/claimed_prizes', response_model=list[ClaimedPrizeReadSchema], tags=['users'])
async def get_claimed_prizes(s: AsyncSession = Depends(get_async_session), user: User = Depends(get_current_user)):
    return await get_user_claimed_prizes(s, user)


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


@app.post('/lootboxes/{lootbox_id}/upload_image', response_model=LootboxReadSchema, tags=['lootboxes'])
async def post_upload_lootbox_image(
        lootbox_id: int,
        file: UploadFile,
        user: User = Depends(get_admin_user),
        s: AsyncSession = Depends(get_async_session)
):
    return await upload_lootbox_image(s, lootbox_id, file)


@app.post('/lootboxes/open', response_model=PrizeReadSchema | None, tags=['lootboxes'])
async def post_open_lootbox(
        schema: LootboxOpenSchema,
        user: User = Depends(get_current_user),
        s: AsyncSession = Depends(get_async_session)
):
    return await open_lootbox(schema, user, s)