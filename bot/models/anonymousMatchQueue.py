from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from bot.config.database import Base
from bot.enums.anonymousMatchQueueStatus import AnonymousMatchQueueStatus


class AnonymousMatchQueue(Base):
    __tablename__ = "anonymous_match_queue"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="anonymous match queue id")
    user_id = Column(
        BigInteger,
        ForeignKey("member.user_id", ondelete="CASCADE"),
        nullable=False,
        comment="discord user id",
    )
    status = Column(
        String(50),
        nullable=False,
        default=AnonymousMatchQueueStatus.WAITING.value,
        comment="queue status: waiting, matched, cancelled",
    )
    created_at = Column(DateTime, nullable=False, server_default=func.now(), comment="created at")
    matched_at = Column(DateTime, nullable=True, comment="matched at")

    member = relationship("Member", foreign_keys=[user_id])
