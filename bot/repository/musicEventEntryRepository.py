from bot.models.musicEventEntry import MusicEventEntry
from collections import OrderedDict


class MusicEventEntryRepository:
    def __init__(self, session):
        self.session = session

    def create(self, userId: int, musicEventId: int, songName: str):
        musicEventEntry = MusicEventEntry(
            user_id=userId,
            music_event_id=musicEventId,
            song_name=songName,
        )
        self.session.add(musicEventEntry)
        self.session.flush()
        return musicEventEntry

    def existsByUserIdAndMusicEventId(self, userId: int, musicEventId: int) -> bool:
        musicEventEntry = (
            self.session.query(MusicEventEntry)
            .filter(MusicEventEntry.user_id == userId)
            .filter(MusicEventEntry.music_event_id == musicEventId)
            .first()
        )
        return musicEventEntry is not None
    
    def createMany(self, userId: int, musicEventId: int, songNames: list[str]):
        musicEventEntries = []

        for songName in songNames:
            musicEventEntry = MusicEventEntry(
                user_id=userId,
                music_event_id=musicEventId,
                song_name=songName,
            )
            self.session.add(musicEventEntry)
            musicEventEntries.append(musicEventEntry)

        self.session.flush()
        return musicEventEntries

    def findGroupedParticipantsByMusicEventId(self, musicEventId: int):
        musicEventEntries = (
            self.session.query(MusicEventEntry)
            .filter(MusicEventEntry.music_event_id == musicEventId)
            .order_by(MusicEventEntry.user_id.asc(), MusicEventEntry.id.asc())
            .all()
        )

        groupedParticipants = OrderedDict()

        for musicEventEntry in musicEventEntries:
            if musicEventEntry.user_id not in groupedParticipants:
                groupedParticipants[musicEventEntry.user_id] = []

            groupedParticipants[musicEventEntry.user_id].append(musicEventEntry.song_name)

        return [
            {
                "userId": userId,
                "songNames": songNames,
            }
            for userId, songNames in groupedParticipants.items()
        ]