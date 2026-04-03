from sqlalchemy import BigInteger, Boolean, Column, DateTime, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from bot.config.database import Base


class MusicEvent(Base):
    __tablename__ = "music_event"

    id = Column(BigInteger, primary_key=True, autoincrement=True, nullable=False)
    event_name = Column(String(255), nullable=False)
    role_id = Column(BigInteger, nullable=False)
    is_available = Column(Boolean, nullable=False, default=True, server_default="1")
    participant_count = Column(Integer, nullable=False, default=0, server_default="0")
    expired_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now())

    musicEventEntries = relationship(
        "MusicEventEntry",
        back_populates="musicEvent",
        cascade="all, delete-orphan",
    )