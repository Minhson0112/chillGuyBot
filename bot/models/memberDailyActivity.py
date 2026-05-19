from sqlalchemy import BigInteger, Column, Date, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from bot.config.database import Base


class MemberDailyActivity(Base):
    __tablename__ = "member_daily_activity"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="member daily activity id")

    user_id = Column(
        BigInteger,
        ForeignKey("member.user_id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        comment="discord user id",
    )

    activity_date = Column(Date, nullable=False, comment="activity date")

    total_chat_count = Column(
        BigInteger,
        nullable=False,
        default=0,
        comment="total chat count in this day",
    )

    level_chat_count = Column(
        BigInteger,
        nullable=False,
        default=0,
        comment="level chat count in this day",
    )

    voice_seconds = Column(
        BigInteger,
        nullable=False,
        default=0,
        comment="total voice connected seconds in this day",
    )

    created_at = Column(
        DateTime,
        nullable=False,
        server_default=func.now(),
        comment="created at",
    )

    updated_at = Column(
        DateTime,
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
        comment="updated at",
    )

    member = relationship("Member", back_populates="dailyActivities")

    __table_args__ = (
        UniqueConstraint("user_id", "activity_date", name="uq_member_daily_activity_user_date"),
    )