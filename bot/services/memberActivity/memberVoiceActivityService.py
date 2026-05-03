from datetime import datetime, time, timedelta, timezone

from bot.cache.memberDailyActivityCache import memberDailyActivityCache
from bot.cache.voiceSessionCache import voiceSessionCache
from bot.config.database import getDbSession
from bot.services.farm.dailyTaskProgressService import DailyTaskProgressService


class MemberVoiceActivityService:
    DAILY_TASK_TYPE_VOICE_TIME = "voice_time"

    def __init__(self):
        self.gmt7 = timezone(timedelta(hours=7))

    def handleVoiceStateUpdate(self, member, before, after):
        if member.bot:
            return None

        if member.guild is None:
            return None

        beforeChannel = before.channel
        afterChannel = after.channel

        if beforeChannel is None and afterChannel is not None:
            self.startVoiceSession(member, afterChannel)
            return None

        if beforeChannel is not None and afterChannel is None:
            return self.endVoiceSession(member)

        if beforeChannel is not None and afterChannel is not None:
            if beforeChannel.id != afterChannel.id:
                self.updateVoiceChannel(member, afterChannel)

        return None

    def startVoiceSession(self, member, channel):
        userId = member.id

        voiceSessionCache[userId] = {
            "joined_at": datetime.now(self.gmt7),
            "channel_id": channel.id,
        }

    def endVoiceSession(self, member):
        userId = member.id

        if userId not in voiceSessionCache:
            return None

        joinedAt = voiceSessionCache[userId]["joined_at"]
        channelId = voiceSessionCache[userId]["channel_id"]
        leftAt = datetime.now(self.gmt7)

        self.addVoiceSecondsToDailyActivity(userId, joinedAt, leftAt)
        dailyTaskMessage = self.addVoiceSecondsToDailyTask(
            userId=userId,
            channelId=channelId,
            startedAt=joinedAt,
            endedAt=leftAt,
        )

        del voiceSessionCache[userId]

        return dailyTaskMessage

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

    def addVoiceSecondsToDailyTask(
        self,
        userId: int,
        channelId: int,
        startedAt,
        endedAt,
    ):
        completedMessages = []
        currentStart = startedAt

        with getDbSession() as session:
            dailyTaskProgressService = DailyTaskProgressService(session)

            while currentStart.date() < endedAt.date():
                nextDay = datetime.combine(
                    currentStart.date() + timedelta(days=1),
                    time.min,
                    tzinfo=self.gmt7,
                )

                voiceSeconds = int((nextDay - currentStart).total_seconds())

                completedTasks = dailyTaskProgressService.addProgress(
                    userId=userId,
                    taskType=self.DAILY_TASK_TYPE_VOICE_TIME,
                    amount=voiceSeconds,
                    targetChannelId=channelId,
                    taskDate=currentStart.date(),
                )

                dailyTaskMessage = dailyTaskProgressService.buildCompletedTaskMessage(
                    completedTasks,
                )

                if dailyTaskMessage is not None:
                    completedMessages.append(dailyTaskMessage)

                currentStart = nextDay

            voiceSeconds = int((endedAt - currentStart).total_seconds())

            completedTasks = dailyTaskProgressService.addProgress(
                userId=userId,
                taskType=self.DAILY_TASK_TYPE_VOICE_TIME,
                amount=voiceSeconds,
                targetChannelId=channelId,
                taskDate=currentStart.date(),
            )

            dailyTaskMessage = dailyTaskProgressService.buildCompletedTaskMessage(
                completedTasks,
            )

            if dailyTaskMessage is not None:
                completedMessages.append(dailyTaskMessage)

            session.commit()

        if not completedMessages:
            return None

        return "\n\n".join(completedMessages)