from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, String
from sqlalchemy.dialects.mysql import BIGINT
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from bot.config.database import Base
from bot.enums.boosterCustomRoleStatus import BoosterCustomRoleStatus


class BoosterCustomRole(Base):
    __tablename__ = "booster_custom_role"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="booster custom role id")

    granted_by_user_id = Column(
        BIGINT(unsigned=True),
        ForeignKey("member.user_id", ondelete="RESTRICT"),
        nullable=False,
        comment="discord user id who granted the role",
    )
    target_user_id = Column(
        BIGINT(unsigned=True),
        ForeignKey("member.user_id", ondelete="RESTRICT"),
        nullable=False,
        comment="discord user id who received the role",
    )
    role_id = Column(BIGINT(unsigned=True), nullable=False, comment="discord custom role id")

    status = Column(
        String(50),
        nullable=False,
        default=BoosterCustomRoleStatus.ACTIVE.value,
        comment="custom role status: active, removed",
    )
    removed_by_user_id = Column(
        BIGINT(unsigned=True),
        ForeignKey("member.user_id", ondelete="SET NULL"),
        nullable=True,
        comment="discord user id who removed the role",
    )
    removed_reason = Column(String(255), nullable=True, comment="removed reason: boost_removed, manual_remove, role_deleted, etc")
    removed_at = Column(DateTime, nullable=True, comment="removed at")

    created_at = Column(DateTime, nullable=False, server_default=func.now(), comment="created at")
    updated_at = Column(
        DateTime,
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
        comment="updated at",
    )

    grantedByMember = relationship("Member", foreign_keys=[granted_by_user_id])
    targetMember = relationship("Member", foreign_keys=[target_user_id])
    removedByMember = relationship("Member", foreign_keys=[removed_by_user_id])
