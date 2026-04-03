from datetime import datetime

from bot.repository.musicEventEntryRepository import MusicEventEntryRepository
from bot.repository.musicEventRepository import MusicEventRepository

class MusicEventService:
    def __init__(self, session):
        self.session = session
        self.musicEventRepository = MusicEventRepository(session)
        self.musicEventEntryRepository = MusicEventEntryRepository(session)

    def findById(self, musicEventId: int):
        return self.musicEventRepository.findById(musicEventId)

    def getAllMusicEvents(self):
        return self.musicEventRepository.findAll()

    def getAvailableMusicEvents(self):
        now = datetime.now()
        return self.musicEventRepository.findAvailableEvents(now)

    def getParticipants(self, musicEventId: int):
        musicEvent = self.musicEventRepository.findById(musicEventId)
        if musicEvent is None:
            return {
                "success": False,
                "message": "Event không tồn tại.",
            }

        participants = self.musicEventEntryRepository.findGroupedParticipantsByMusicEventId(
            musicEventId
        )

        return {
            "success": True,
            "musicEvent": musicEvent,
            "participants": participants,
        }

    def registerSongs(self, userId: int, musicEventId: int, rawSongNames: str):
        musicEvent = self.musicEventRepository.findById(musicEventId)

        if musicEvent is None:
            return {
                "success": False,
                "message": "Event không tồn tại.",
            }

        if not musicEvent.is_available:
            return {
                "success": False,
                "message": "Event đã đóng đăng kí.",
            }

        if musicEvent.expired_at <= datetime.now():
            return {
                "success": False,
                "message": "Event đã hết hạn đăng kí.",
            }

        songNames = []
        for songName in rawSongNames.split(","):
            normalizedSongName = songName.strip()
            if normalizedSongName:
                songNames.append(normalizedSongName)

        if not songNames:
            return {
                "success": False,
                "message": "Bạn chưa nhập tên bài hát hợp lệ.",
            }

        isFirstJoin = not self.musicEventEntryRepository.existsByUserIdAndMusicEventId(
            userId=userId,
            musicEventId=musicEventId,
        )

        musicEventEntries = self.musicEventEntryRepository.createMany(
            userId=userId,
            musicEventId=musicEventId,
            songNames=songNames,
        )

        if isFirstJoin:
            self.musicEventRepository.increaseParticipantCount(musicEvent)

        self.session.commit()

        return {
            "success": True,
            "message": "Đăng kí bài hát thành công.",
            "musicEvent": musicEvent,
            "musicEventEntries": musicEventEntries,
            "isFirstJoin": isFirstJoin,
        }