from sqlalchemy import BigInteger, Boolean, Column, Date, DateTime, String
from sqlalchemy.orm import relationship

from bot.config.database import Base


class Member(Base):
    __tablename__ = "member"

    user_id = Column(BigInteger, primary_key=True, comment="id discord bot")
    global_name = Column(String(255), nullable=True, comment="global name in discord")
    username = Column(String(255), nullable=False, comment="username in discord")
    nick = Column(String(255), nullable=True, comment="username in chill station")
    date_of_birth = Column(Date, nullable=True, comment="date of birth")
    joined_at = Column(DateTime, nullable=False, comment="join chill station at")
    leave_at = Column(DateTime, nullable=True, comment="leave chill station at")
    is_bot = Column(Boolean, nullable=False, comment="is bot?")

    chat = relationship("Chat", back_populates="member", uselist=False)
    tournamentEntries = relationship("TournamentEntry", back_populates="member")