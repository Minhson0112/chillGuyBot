from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from bot.config.database import Base


class FarmCookingHistory(Base):
    __tablename__ = "farm_cooking_histories"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="farm cooking history id")
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
        comment="received food item id",
    )
    quantity = Column(Integer, nullable=False, comment="received quantity")
    received_at = Column(DateTime, nullable=False, server_default=func.now(), comment="received at")

    member = relationship("Member", back_populates="cookingHistories")
    item = relationship("Item", back_populates="cookingHistories")
