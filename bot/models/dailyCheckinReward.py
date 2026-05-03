from sqlalchemy import BigInteger, Boolean, Column, DateTime, ForeignKey, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from bot.config.database import Base


class DailyCheckinReward(Base):
    __tablename__ = "daily_checkin_rewards"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="daily checkin reward id")

    streak_day = Column(Integer, nullable=False, unique=True, comment="streak day from 1 to 7")

    reward_chill_coin = Column(
        BigInteger,
        nullable=False,
        default=0,
        comment="reward chill coin",
    )

    reward_item_id = Column(
        BigInteger,
        ForeignKey("items.id", ondelete="RESTRICT"),
        nullable=True,
        comment="reward item id",
    )

    reward_item_quantity = Column(
        BigInteger,
        nullable=False,
        default=0,
        comment="reward item quantity",
    )

    is_active = Column(Boolean, nullable=False, default=True, comment="whether reward is active")

    created_at = Column(DateTime, nullable=False, server_default=func.now(), comment="created at")
    updated_at = Column(
        DateTime,
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
        comment="updated at",
    )

    rewardItem = relationship("Item", back_populates="dailyCheckinRewards")