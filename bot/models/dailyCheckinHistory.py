from sqlalchemy import BigInteger, Column, Date, DateTime, ForeignKey, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from bot.config.database import Base


class DailyCheckinHistory(Base):
    __tablename__ = "daily_checkin_histories"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="daily checkin history id")

    user_id = Column(
        BigInteger,
        ForeignKey("member.user_id", ondelete="CASCADE"),
        nullable=False,
        comment="discord user id",
    )

    checkin_date = Column(Date, nullable=False, comment="checkin date")

    streak_day = Column(Integer, nullable=False, comment="streak day when checked in")

    reward_chill_coin = Column(
        BigInteger,
        nullable=False,
        default=0,
        comment="received chill coin snapshot",
    )

    reward_item_id = Column(
        BigInteger,
        ForeignKey("items.id", ondelete="RESTRICT"),
        nullable=True,
        comment="received item id snapshot",
    )

    reward_item_quantity = Column(
        BigInteger,
        nullable=False,
        default=0,
        comment="received item quantity snapshot",
    )

    created_at = Column(DateTime, nullable=False, server_default=func.now(), comment="created at")

    member = relationship("Member", back_populates="dailyCheckinHistories")
    rewardItem = relationship("Item", back_populates="dailyCheckinHistories")