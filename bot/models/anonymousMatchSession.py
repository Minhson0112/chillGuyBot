from sqlalchemy import BigInteger, Boolean, Column, DateTime, ForeignKey, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from bot.config.database import Base
from bot.enums.anonymousMatchSessionStatus import AnonymousMatchSessionStatus


class AnonymousMatchSession(Base):
    __tablename__ = "anonymous_match_sessions"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="anonymous match session id")

    user_a_id = Column(
        BigInteger,
        ForeignKey("member.user_id", ondelete="CASCADE"),
        nullable=False,
        comment="first discord user id",
    )
    user_b_id = Column(
        BigInteger,
        ForeignKey("member.user_id", ondelete="CASCADE"),
        nullable=False,
        comment="second discord user id",
    )
    user_a_alias = Column(String(32), nullable=False, comment="first user anonymous alias")
    user_b_alias = Column(String(32), nullable=False, comment="second user anonymous alias")

    status = Column(
        String(50),
        nullable=False,
        default=AnonymousMatchSessionStatus.ACTIVE.value,
        comment="session status: active, ending_requested, ended",
    )
    end_requested_by_a = Column(Boolean, nullable=False, default=False, comment="first user requested ending")
    end_requested_by_b = Column(Boolean, nullable=False, default=False, comment="second user requested ending")

    created_at = Column(DateTime, nullable=False, server_default=func.now(), comment="created at")
    ended_at = Column(DateTime, nullable=True, comment="ended at")

    userA = relationship("Member", foreign_keys=[user_a_id])
    userB = relationship("Member", foreign_keys=[user_b_id])
