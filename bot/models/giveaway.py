from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from bot.config.database import Base
from bot.enums.giveawayStatus import GiveawayStatus


class Giveaway(Base):
    __tablename__ = "giveaway"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="giveaway id")

    type = Column(String(50), nullable=False, comment="giveaway type: chill_coin, cowoncy, vnd, custom")
    title = Column(String(255), nullable=True, comment="giveaway title")
    winner_count = Column(Integer, nullable=False, default=1, comment="number of winners")
    reward_chill_coin = Column(BigInteger, nullable=True, comment="reward chill coin amount")
    reward_cowoncy = Column(BigInteger, nullable=True, comment="reward cowoncy amount")
    reward_vnd = Column(BigInteger, nullable=True, comment="reward vnd amount")
    reward_text = Column(Text, nullable=True, comment="custom reward description")

    status = Column(String(50), nullable=False, default=GiveawayStatus.ACTIVE.value, comment="giveaway status: active, cancelled, ended")

    duration_seconds = Column(BigInteger, nullable=False, comment="giveaway duration in seconds")
    draw_at = Column(DateTime, nullable=False, comment="scheduled draw datetime")
    ended_at = Column(DateTime, nullable=True, comment="ended at")
    cancelled_at = Column(DateTime, nullable=True, comment="cancelled at")

    channel_id = Column(BigInteger, nullable=False, comment="discord channel id")
    message_id = Column(BigInteger, nullable=True, comment="discord giveaway message id")
    created_by_user_id = Column(
        BigInteger,
        ForeignKey("member.user_id", ondelete="RESTRICT"),
        nullable=False,
        comment="discord user id who created giveaway",
    )
    cancelled_by_user_id = Column(
        BigInteger,
        ForeignKey("member.user_id", ondelete="SET NULL"),
        nullable=True,
        comment="discord user id who cancelled giveaway",
    )
    limit_role_id = Column(BigInteger, nullable=True, comment="required discord role id to join giveaway")

    created_at = Column(DateTime, nullable=False, server_default=func.now(), comment="created at")
    updated_at = Column(
        DateTime,
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
        comment="updated at",
    )

    createdByMember = relationship("Member", foreign_keys=[created_by_user_id])
    cancelledByMember = relationship("Member", foreign_keys=[cancelled_by_user_id])
    participants = relationship(
        "GiveawayParticipant",
        back_populates="giveaway",
        cascade="all, delete-orphan",
    )
    winners = relationship(
        "GiveawayWinner",
        foreign_keys="GiveawayWinner.giveaway_id",
        back_populates="giveaway",
        cascade="all, delete-orphan",
    )
