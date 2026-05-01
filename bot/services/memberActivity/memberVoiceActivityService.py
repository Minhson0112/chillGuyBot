from datetime import datetime, time, timedelta, timezone

from bot.cache.memberDailyActivityCache import memberDailyActivityCache
from bot.cache.voiceSessionCache import voiceSessionCache


class MemberVoiceActivityService:
    def __init__(self):
        self.gmt7 = timezone(timedelta(hours=7))

    def handleVoiceStateUpdate(self, member, before, after):
        if member.bot:
            return

        if member.guild is None:
            return

        beforeChannel = before.channel
        afterChannel = after.channel

        if beforeChannel is None and afterChannel is not None:
            self.startVoiceSession(member, afterChannel)
            return

        if beforeChannel is not None and afterChannel is None:
            self.endVoiceSession(member)
            return

        if beforeChannel is not None and afterChannel is not None:
            if beforeChannel.id != afterChannel.id:
                self.updateVoiceChannel(member, afterChannel)

    def startVoiceSession(self, member, channel):
        userId = member.id

        voiceSessionCache[userId] = {
            "joined_at": datetime.now(self.gmt7),
            "channel_id": channel.id,
        }

    def endVoiceSession(self, member):
        userId = member.id

        if userId not in voiceSessionCache:
            return

        joinedAt = voiceSessionCache[userId]["joined_at"]
        leftAt = datetime.now(self.gmt7)

        self.addVoiceSecondsToDailyActivity(userId, joinedAt, leftAt)

        del voiceSessionCache[userId]

    def updateVoiceChannel(self, member, channel):
        userId = member.id

        if userId not in voiceSessionCache:
            voiceSessionCache[userId] = {
                "joined_at": datetime.now(self.gmt7),
                "channel_id": channel.id,
            }
            return

        voiceSessionCache[userId]["channel_id"] = channel.id

    def addVoiceSecondsToDailyActivity(self, userId, startedAt, endedAt):
        currentStart = startedAt

        while currentStart.date() < endedAt.date():
            nextDay = datetime.combine(
                currentStart.date() + timedelta(days=1),
                time.min,
                tzinfo=self.gmt7,
            )

            voiceSeconds = int((nextDay - currentStart).total_seconds())
            self.addVoiceSeconds(userId, currentStart.date(), voiceSeconds)

            currentStart = nextDay

        voiceSeconds = int((endedAt - currentStart).total_seconds())
        self.addVoiceSeconds(userId, currentStart.date(), voiceSeconds)

    def addVoiceSeconds(self, userId, activityDate, voiceSeconds):
        if voiceSeconds <= 0:
            return

        cacheKey = (userId, activityDate)

        if cacheKey not in memberDailyActivityCache:
            memberDailyActivityCache[cacheKey] = {
                "total_chat_count": 0,
                "level_chat_count": 0,
                "voice_seconds": 0,
            }

        memberDailyActivityCache[cacheKey]["voice_seconds"] += voiceSeconds