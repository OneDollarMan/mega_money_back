import asyncio
from decimal import Decimal
from config import PrizeQualityEnum, PrizeTypeEnum
from db import async_session_maker
from models import Prize, Lootbox


lootboxes_data = [
    {
        "name": "Basic Lootbox",
        "open_price": Decimal("5.00"),
        "prizes": [
            {"name": "Common Token", "quality": PrizeQualityEnum.common, "drop_chance": Decimal("0.5"), "type": PrizeTypeEnum.TOKENS, "tokens_amount": Decimal("10.00")},
            {"name": "Uncommon Token", "quality": PrizeQualityEnum.uncommon, "drop_chance": Decimal("0.3"), "type": PrizeTypeEnum.TOKENS, "tokens_amount": Decimal("20.00")},
            {"name": "Rare Token", "quality": PrizeQualityEnum.rare, "drop_chance": Decimal("0.15"), "type": PrizeTypeEnum.TOKENS, "tokens_amount": Decimal("50.00")},
            {"name": "Epic Token", "quality": PrizeQualityEnum.epic, "drop_chance": Decimal("0.04"), "type": PrizeTypeEnum.TOKENS, "tokens_amount": Decimal("100.00")},
            {"name": "Legendary Token", "quality": PrizeQualityEnum.legendary, "drop_chance": Decimal("0.01"), "type": PrizeTypeEnum.TOKENS, "tokens_amount": Decimal("200.00")},
        ]
    },
    {
        "name": "Premium Lootbox",
        "open_price": Decimal("10.00"),
        "prizes": [
            {"name": "Uncommon Token", "quality": PrizeQualityEnum.uncommon, "drop_chance": Decimal("0.4"), "type": PrizeTypeEnum.TOKENS, "tokens_amount": Decimal("20.00")},
            {"name": "Rare Token", "quality": PrizeQualityEnum.rare, "drop_chance": Decimal("0.3"), "type": PrizeTypeEnum.TOKENS, "tokens_amount": Decimal("50.00")},
            {"name": "Epic Token", "quality": PrizeQualityEnum.epic, "drop_chance": Decimal("0.2"), "type": PrizeTypeEnum.TOKENS, "tokens_amount": Decimal("100.00")},
            {"name": "Legendary Token", "quality": PrizeQualityEnum.legendary, "drop_chance": Decimal("0.1"), "type": PrizeTypeEnum.TOKENS, "tokens_amount": Decimal("200.00")},
        ]
    }
]


async def fill_db():
    async with async_session_maker() as session:
        ...
        for lootbox_data in lootboxes_data:
            lootbox = Lootbox(
                name=lootbox_data["name"],
                open_price=lootbox_data["open_price"]
            )
            session.add(lootbox)

            for prize_data in lootbox_data["prizes"]:
                prize = Prize(
                    name=prize_data["name"],
                    quality=prize_data["quality"].value,
                    drop_chance=prize_data["drop_chance"],
                    type=prize_data["type"].value,
                    lootbox=lootbox,
                    tokens_amount=prize_data["tokens_amount"]
                )
                session.add(prize)

        await session.commit()


asyncio.run(fill_db())