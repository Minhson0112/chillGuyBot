from sqlalchemy import BigInteger, Column, Date, DateTime, ForeignKey, Integer, Text, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from bot.config.database import Base


class MemberDailyFortune(Base):
    __tablename__ = "member_daily_fortune"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="member daily fortune id")

    user_id = Column(
        BigInteger,
        ForeignKey("member.user_id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        comment="discord user id",
    )

    fortune_date = Column(Date, nullable=False, comment="fortune date")

    love_rate = Column(
        Integer,
        nullable=False,
        comment="love fortune rate from 0 to 100",
    )

    luck_rate = Column(
        Integer,
        nullable=False,
        comment="luck fortune rate from 0 to 100",
    )

    career_rate = Column(
        Integer,
        nullable=False,
        comment="career or study fortune rate from 0 to 100",
    )

    description = Column(Text, nullable=False, comment="AI generated fortune description")

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

    member = relationship("Member", back_populates="dailyFortunes")

    __table_args__ = (
        UniqueConstraint("user_id", "fortune_date", name="uq_member_daily_fortune_user_date"),
    )
