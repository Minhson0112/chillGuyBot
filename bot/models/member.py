from sqlalchemy import BigInteger, Boolean, Column, Date, Integer, DateTime, String
from sqlalchemy.orm import relationship

from bot.config.database import Base


class Member(Base):
    __tablename__ = "member"

    user_id = Column(BigInteger, primary_key=True, comment="id discord")
    global_name = Column(String(255), nullable=True, comment="global name in discord")
    username = Column(String(255), nullable=False, comment="username in discord")
    nick = Column(String(255), nullable=True, comment="username in chill station")
    date_of_birth = Column(Date, nullable=True, comment="date of birth")
    joined_at = Column(DateTime, nullable=False, comment="join chill station at")
    leave_at = Column(DateTime, nullable=True, comment="leave chill station at")
    is_bot = Column(Boolean, nullable=False, comment="is bot?")
    join_count = Column(Integer, nullable=False, default=1, comment="number of times the member has joined the server")
    warning_count = Column(Integer, nullable=False, default=0, comment="number of warnings for rule violations")

    chat = relationship("Chat", back_populates="member", uselist=False)
    tournamentEntries = relationship("TournamentEntry", back_populates="member")
    moderationActions = relationship("MemberModerationHistory", foreign_keys="MemberModerationHistory.action_by_user_id", back_populates="actionByMember")
    moderationTargets = relationship("MemberModerationHistory", foreign_keys="MemberModerationHistory.target_user_id", back_populates="targetMember")