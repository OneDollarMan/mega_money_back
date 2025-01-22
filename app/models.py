import uuid
from decimal import Decimal
from datetime import datetime
from sqlalchemy import UUID, Text, Double, Integer, ForeignKey, DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, relationship, mapped_column


class Base(DeclarativeBase):
    ...


class User(Base):
    __tablename__ = 'users'

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    address: Mapped[str] = mapped_column(Text)
    name: Mapped[str | None] = mapped_column(Text, nullable=True)
    balance: Mapped[Decimal] = mapped_column(Double, default=Decimal(0))

    claimed_prizes: Mapped[list['ClaimedPrize']] = relationship('ClaimedPrize', back_populates='user')


class Prize(Base):
    __tablename__ = 'prizes'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(Text)
    quality: Mapped[str] = mapped_column(Text)
    drop_chance: Mapped[Decimal] = mapped_column(Double)
    type: Mapped[str] = mapped_column(Text)
    lootbox_id: Mapped[int] = mapped_column(ForeignKey('lootboxes.id'))
    tokens_amount: Mapped[Decimal] = mapped_column(Double, default=Decimal(0))

    lootbox: Mapped['Lootbox'] = relationship('Lootbox', back_populates='prizes')


class Lootbox(Base):
    __tablename__ = 'lootboxes'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(Text)
    image_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    open_price: Mapped[Decimal] = mapped_column(Double)

    prizes: Mapped[list[Prize]] = relationship(Prize, back_populates='lootbox')


class ClaimedPrize(Base):
    __tablename__ = 'claimed_prizes'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    prize_id: Mapped[int] = mapped_column(ForeignKey('prizes.id'))
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    claim_date: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    prize: Mapped['Prize'] = relationship('Prize')
    user: Mapped['User'] = relationship('User', back_populates='claimed_prizes')
