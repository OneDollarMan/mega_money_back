import uuid
from decimal import Decimal

from sqlalchemy import UUID, Text, Double, Integer, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, relationship
from sqlalchemy.testing.schema import mapped_column


class Base(DeclarativeBase):
    ...


class User(Base):
    __tablename__ = 'users'

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    address: Mapped[str] = mapped_column(Text)
    name: Mapped[str] = mapped_column(Text, nullable=True)
    balance: Mapped[Decimal] = mapped_column(Double, default=Decimal(0))


class Prize(Base):
    __tablename__ = 'prizes'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(Text, nullable=True)
    lootbox_id: Mapped[int] = mapped_column(ForeignKey('lootboxes.id'))

    lootbox: Mapped['Lootbox'] = relationship('Lootbox', back_populates='prizes')


class Lootbox(Base):
    __tablename__ = 'lootboxes'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(Text, nullable=True)

    prizes: Mapped[list[Prize]] = relationship(Prize, back_populates='lootbox')