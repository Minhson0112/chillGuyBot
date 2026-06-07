from sqlalchemy import BigInteger, Boolean, Column, DateTime, ForeignKey, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from bot.config.database import Base
from bot.enums.serverInviteStatus import ServerInviteStatus


class ServerInvite(Base):
    __tablename__ = "server_invites"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="server invite id")

    invite_code = Column(String(32), nullable=False, unique=True, comment="discord invite code")
    invite_url = Column(String(255), nullable=False, comment="discord invite url")

    channel_id = Column(BigInteger, nullable=True, comment="discord channel id")
    inviter_user_id = Column(
        BigInteger,
        ForeignKey("member.user_id", ondelete="SET NULL", onupdate="CASCADE"),
        nullable=True,
        comment="discord user id who created invite",
    )

    uses = Column(BigInteger, nullable=False, default=0, comment="current invite uses from discord")
    max_uses = Column(BigInteger, nullable=False, default=0, comment="max uses, 0 means unlimited")
    max_age = Column(BigInteger, nullable=False, default=0, comment="max age seconds, 0 means never expire")
    temporary = Column(Boolean, nullable=False, default=False, comment="temporary membership invite")

    status = Column(
        String(50),
        nullable=False,
        default=ServerInviteStatus.ACTIVE.value,
        comment="invite status: active, expired, deleted, unknown",
    )

    discord_created_at = Column(DateTime, nullable=True, comment="invite created at from discord")
    expired_at = Column(DateTime, nullable=True, comment="calculated invite expired at")
    deleted_at = Column(DateTime, nullable=True, comment="invite deleted at")
    last_fetched_at = Column(DateTime, nullable=True, comment="last fetched from discord")

    created_at = Column(DateTime, nullable=False, server_default=func.now(), comment="created at")
    updated_at = Column(
        DateTime,
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
        comment="updated at",
    )

    inviter = relationship("Member", foreign_keys=[inviter_user_id])
