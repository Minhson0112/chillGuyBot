from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from bot.config.database import Base


class GiveawayParticipant(Base):
    __tablename__ = "giveaway_participants"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="giveaway participant id")

    giveaway_id = Column(
        BigInteger,
        ForeignKey("giveaway.id", ondelete="CASCADE"),
        nullable=False,
        comment="giveaway id",
    )
    user_id = Column(
        BigInteger,
        ForeignKey("member.user_id", ondelete="CASCADE"),
        nullable=False,
        comment="discord user id",
    )

    status = Column(String(50), nullable=False, default="active", comment="participant status: active, removed, invalid")
    invalid_reason = Column(String(255), nullable=True, comment="invalid reason: missing_role, left_server, bot_user, manual_remove, etc")

    joined_at = Column(DateTime, nullable=False, server_default=func.now(), comment="joined at")
    created_at = Column(DateTime, nullable=False, server_default=func.now(), comment="created at")
    updated_at = Column(
        DateTime,
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
        comment="updated at",
    )

    giveaway = relationship("Giveaway", back_populates="participants")
    member = relationship("Member", foreign_keys=[user_id])
