from sqlalchemy import CheckConstraint, Column, DateTime, ForeignKey, Index, UniqueConstraint
from sqlalchemy.dialects.mysql import BIGINT
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from bot.config.database import Base


class Couple(Base):
    __tablename__ = "couple"
    __table_args__ = (
        UniqueConstraint("user_1_id", "user_2_id", name="uq_couple_users"),
        Index("idx_couple_user_2_id", "user_2_id"),
        Index("idx_couple_divorcing_at", "divorcing_at"),
        CheckConstraint(
            "user_1_id <> user_2_id",
            name="chk_couple_distinct_users",
        ),
    )

    id = Column(BIGINT, primary_key=True, autoincrement=True, comment="couple id")
    user_1_id = Column(
        BIGINT(unsigned=True),
        ForeignKey("member.user_id", ondelete="RESTRICT"),
        nullable=False,
        comment="first discord user id",
    )
    user_2_id = Column(
        BIGINT(unsigned=True),
        ForeignKey("member.user_id", ondelete="RESTRICT"),
        nullable=False,
        comment="second discord user id",
    )
    intimacy_points = Column(
        BIGINT(unsigned=True),
        nullable=False,
        default=0,
        comment="couple intimacy points",
    )
    created_at = Column(DateTime, nullable=False, server_default=func.now(), comment="created at")
    divorcing_at = Column(DateTime, nullable=True, comment="divorcing at")
    couple_role_id = Column(
        BIGINT(unsigned=True),
        nullable=True,
        comment="discord couple role id",
    )

    user1 = relationship("Member", foreign_keys=[user_1_id])
    user2 = relationship("Member", foreign_keys=[user_2_id])
    dailyVoiceActivities = relationship(
        "CoupleDailyVoiceActivity",
        back_populates="couple",
    )
