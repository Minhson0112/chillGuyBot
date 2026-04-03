from sqlalchemy import asc, desc
from datetime import datetime

from bot.models.musicEvent import MusicEvent


class MusicEventRepository:
    def __init__(self, session):
        self.session = session

    def create(self, eventName: str, roleId: int, expiredAt):
        musicEvent = MusicEvent(
            event_name=eventName,
            role_id=roleId,
            is_available=True,
            participant_count=0,
            expired_at=expiredAt,
        )
        self.session.add(musicEvent)
        self.session.flush()
        return musicEvent

    def findAvailableEvents(self, now):
        return (
            self.session.query(MusicEvent)
            .filter(MusicEvent.is_available.is_(True))
            .filter(MusicEvent.expired_at > now)
            .order_by(asc(MusicEvent.expired_at), asc(MusicEvent.id))
            .all()
        )

    def findById(self, musicEventId: int):
        return (
            self.session.query(MusicEvent)
            .filter(MusicEvent.id == musicEventId)
            .first()
        )

    def findAll(self):
        return (
            self.session.query(MusicEvent)
            .order_by(desc(MusicEvent.created_at), desc(MusicEvent.id))
            .all()
        )

    def increaseParticipantCount(self, musicEvent):
        musicEvent.participant_count += 1
        self.session.flush()
        return musicEvent

    def findAllOpenEvents(self):
        return (
            self.session.query(MusicEvent)
            .filter(MusicEvent.is_available.is_(True))
            .filter(MusicEvent.expired_at > datetime.now())
            .all()
        )

    def closeEvent(self, musicEvent: MusicEvent):
        musicEvent.is_available = False
        self.session.flush()
        return musicEvent