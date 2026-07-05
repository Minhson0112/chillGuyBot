from sqlalchemy import Column, Date, DateTime, ForeignKey, Index, UniqueConstraint
from sqlalchemy.dialects.mysql import BIGINT
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from bot.config.database import Base


class CoupleDailyVoiceActivity(Base):
    __tablename__ = "couple_daily_voice_activity"
    __table_args__ = (
        UniqueConstraint(
            "couple_id",
            "activity_date",
            name="uq_couple_daily_voice_activity_couple_date",
        ),
        Index(
            "idx_couple_daily_voice_activity_date_voice",
            "activity_date",
            "voice_seconds",
        ),
    )

    id = Column(BIGINT, primary_key=True, autoincrement=True, comment="couple daily voice activity id")
    couple_id = Column(
        BIGINT,
        ForeignKey("couple.id", ondelete="RESTRICT"),
        nullable=False,
        comment="couple id",
    )
    activity_date = Column(Date, nullable=False, comment="activity date in GMT+7")
    voice_seconds = Column(
        BIGINT(unsigned=True),
        nullable=False,
        default=0,
        comment="seconds both users were in the same voice channel",
    )
    created_at = Column(DateTime, nullable=False, server_default=func.now(), comment="created at")
    updated_at = Column(
        DateTime,
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
        comment="updated at",
    )

    couple = relationship("Couple", back_populates="dailyVoiceActivities")
