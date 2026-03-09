from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, Integer, String, text
from sqlalchemy.orm import relationship

from bot.config.database import Base


class MemberModerationHistory(Base):
    __tablename__ = "member_moderation_history"

    id_member_moderation_history = Column(BigInteger, primary_key=True, autoincrement=True)
    action_by_user_id = Column(BigInteger, ForeignKey("member.user_id"), nullable=False, comment="member id who performed the moderation action")
    target_user_id = Column(BigInteger, ForeignKey("member.user_id"), nullable=False, comment="member id who received the moderation action")
    action_type = Column(Integer, nullable=False, comment="1: mute, 2: kick, 3: ban")
    reason = Column(String(500), nullable=True, comment="reason for moderation action")
    duration_minutes = Column(Integer, nullable=True, comment="duration in minutes for temporary moderation actions")
    created_at = Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"), comment="created at")

    actionByMember = relationship("Member",foreign_keys=[action_by_user_id])
    targetMember = relationship("Member",foreign_keys=[target_user_id])