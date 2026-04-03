from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from bot.config.database import Base


class MusicEventEntry(Base):
    __tablename__ = "music_event_entry"

    id = Column(BigInteger, primary_key=True, autoincrement=True, nullable=False)
    user_id = Column(
        BigInteger,
        ForeignKey("member.user_id", name="fk_music_event_entry_user_id"),
        nullable=False,
    )
    music_event_id = Column(
        BigInteger,
        ForeignKey("music_event.id", name="fk_music_event_entry_music_event_id"),
        nullable=False,
    )
    song_name = Column(String(255), nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now())

    member = relationship("Member", back_populates="musicEventEntries")
    musicEvent = relationship("MusicEvent", back_populates="musicEventEntries")