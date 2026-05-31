import discord

from bot.services.anonymousMatch.anonymousMatchCacheService import AnonymousMatchCacheService


class AnonymousMatchMessageRelayService:
    def __init__(self):
        self.anonymousMatchCacheService = AnonymousMatchCacheService()

    async def relayMessage(self, bot, message: discord.Message):
        if message.guild is not None:
            return False

        if message.content.startswith("cg ") or message.content.startswith("Cg "):
            return False

        matchData = self.anonymousMatchCacheService.findByUserId(message.author.id)
        if matchData is None:
            return False

        relayContent = self.buildRelayContent(message, matchData["alias"])
        if relayContent is None:
            return False

        try:
            partnerUser = bot.get_user(matchData["partnerUserId"]) or await bot.fetch_user(matchData["partnerUserId"])
            await partnerUser.send(relayContent)
            return True
        except discord.HTTPException:
            return False

    def buildRelayContent(self, message: discord.Message, alias):
        messageParts = []

        if message.content:
            messageParts.append(message.content)

        for attachment in message.attachments:
            messageParts.append(attachment.url)

        if len(messageParts) == 0:
            return None

        return f"{alias}: " + "\n".join(messageParts)
