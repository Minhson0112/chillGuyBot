from sqlalchemy import BigInteger, Boolean, Column, DateTime, ForeignKey, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from bot.config.database import Base


class FarmHarvestHistory(Base):
    __tablename__ = "farm_harvest_histories"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="farm harvest history id")
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
        comment="harvested crop item id",
    )
    quantity = Column(Integer, nullable=False, comment="harvested quantity including tool bonus")
    is_perfect_harvest = Column(
        Boolean,
        nullable=False,
        default=False,
        comment="whether no crops were lost to pests, dryness, or theft",
    )
    harvested_at = Column(DateTime, nullable=False, server_default=func.now(), comment="harvested at")

    member = relationship("Member", back_populates="harvestHistories")
    item = relationship("Item", back_populates="harvestHistories")
