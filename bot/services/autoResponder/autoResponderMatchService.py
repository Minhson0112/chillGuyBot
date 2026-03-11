from bot.cache.autoResponderCache import autoResponderKeyCache
from bot.config.database import getDbSession
from bot.repository.autoResponderRepository import AutoResponderRepository


class AutoResponderMatchService:
    def findMatchedKey(self, content):
        contentLower = content.lower()

        for msgKey in autoResponderKeyCache:
            if msgKey in contentLower:
                return msgKey

        return None

    def findAutoResponderByMatchedKey(self, matchedKey):
        if matchedKey is None:
            return None

        with getDbSession() as session:
            autoResponderRepository = AutoResponderRepository(session)
            return autoResponderRepository.findByMsgKey(matchedKey)

    def canUseAutoResponder(self, autoResponder, userId):
        if autoResponder is None:
            return False

        if autoResponder.user_id == userId:
            return True

        if autoResponder.is_global:
            return True

        return False

    def parseMessageLink(self, messageLink):
        parts = messageLink.strip().split("/")
        guildId = int(parts[-3])
        channelId = int(parts[-2])
        messageId = int(parts[-1])
        return guildId, channelId, messageId

    async def fetchTemplateMessage(self, bot, messageLink):
        guildId, channelId, messageId = self.parseMessageLink(messageLink)

        channel = bot.get_channel(channelId)
        if channel is None:
            channel = await bot.fetch_channel(channelId)

        return await channel.fetch_message(messageId)