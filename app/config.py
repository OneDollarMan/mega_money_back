import os
from enum import Enum

#DATABASE CONFIG
PG_USER = os.getenv("POSTGRES_USER")
PG_PASSWORD = os.getenv("POSTGRES_PASSWORD")
PG_HOST = os.getenv("POSTGRES_HOST")
PG_PORT = os.getenv("POSTGRES_PORT")
PG_DB = os.getenv("POSTGRES_DB")
DATABASE_URL = f'postgresql+asyncpg://{PG_USER}:{PG_PASSWORD}@{PG_HOST}:{PG_PORT}/{PG_DB}'

#JWT TOKEN CONFIG
SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS = 1

STATIC_PATH = '../static'
CHUNK_SIZE = 5 * 1024 * 1024  # 5 MB
PLATFORM_URL = 'http://127.0.0.1'


class PrizeQualityEnum(Enum):
    common = 'Common'
    uncommon = 'Uncommon'
    rare = 'Rare'
    epic = 'Epic'
    legendary = 'Legendary'


class PrizeTypeEnum(Enum):
    TOKENS = 'Tokens'
    NFT = 'NFT'