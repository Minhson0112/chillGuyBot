from bot.cache.chatCountCache import chatCountCache
from bot.config.channel import EXCLUDED_LEVEL_CHANNEL_IDS


class ChatCountService:
    def addMessageCount(self, message):
        if message.author.bot:
            return

        if message.guild is None:
            return

        userId = message.author.id
        channelId = message.channel.id

        if userId not in chatCountCache:
            chatCountCache[userId] = {
                "total_chat_count": 0,
                "level_chat_count": 0,
            }

        chatCountCache[userId]["total_chat_count"] += 1

        if channelId not in EXCLUDED_LEVEL_CHANNEL_IDS:
            chatCountCache[userId]["level_chat_count"] += 1