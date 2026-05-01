from datetime import datetime, timedelta, timezone

from bot.cache.memberDailyActivityCache import memberDailyActivityCache
from bot.config.channel import EXCLUDED_LEVEL_CHANNEL_IDS


class MemberDailyActivityService:
    def __init__(self):
        self.gmt7 = timezone(timedelta(hours=7))

    def addChatActivity(self, message):
        if message.author.bot:
            return

        if message.guild is None:
            return

        userId = message.author.id
        channelId = message.channel.id
        activityDate = datetime.now(self.gmt7).date()

        cacheKey = (userId, activityDate)

        if cacheKey not in memberDailyActivityCache:
            memberDailyActivityCache[cacheKey] = {
                "total_chat_count": 0,
                "level_chat_count": 0,
                "voice_seconds": 0,
            }

        memberDailyActivityCache[cacheKey]["total_chat_count"] += 1

        if channelId not in EXCLUDED_LEVEL_CHANNEL_IDS:
            memberDailyActivityCache[cacheKey]["level_chat_count"] += 1