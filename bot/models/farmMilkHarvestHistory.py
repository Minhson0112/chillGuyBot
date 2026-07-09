from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from bot.config.database import Base


class FarmMilkHarvestHistory(Base):
    __tablename__ = "farm_milk_harvest_histories"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="farm milk harvest history id")
    user_id = Column(
        BigInteger,
        ForeignKey("member.user_id", ondelete="CASCADE"),
        nullable=False,
        comment="discord user id of the farm owner",
    )
    item_id = Column(
        BigInteger,
        ForeignKey("items.id", ondelete="RESTRICT"),
        nullable=False,
        comment="harvested milk item id",
    )
    quantity = Column(Integer, nullable=False, comment="harvested milk quantity")
    harvested_at = Column(DateTime, nullable=False, server_default=func.now(), comment="harvested at")

    member = relationship("Member", back_populates="milkHarvestHistories")
    item = relationship("Item", back_populates="milkHarvestHistories")
