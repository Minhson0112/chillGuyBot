from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from bot.config.database import Base


class FishingHistory(Base):
    __tablename__ = "fishing_history"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="fishing history id")

    user_id = Column(
        BigInteger,
        ForeignKey("member.user_id", ondelete="CASCADE"),
        nullable=False,
        comment="discord user id",
    )

    item_id = Column(
        BigInteger,
        ForeignKey("items.id", ondelete="RESTRICT"),
        nullable=False,
        comment="caught seafood item id",
    )

    weight_kg = Column(Numeric(5, 2), nullable=False, comment="caught seafood weight in kg")

    caught_at = Column(DateTime, nullable=False, server_default=func.now(), comment="caught at")

    member = relationship("Member", back_populates="fishingHistories")
    item = relationship("Item", back_populates="fishingHistories")