import discord
from discord.ext import commands

from bot.services.anonymousMatch.anonymousMatchMessageRelayService import AnonymousMatchMessageRelayService


class AnonymousMatchMessageRelayEvent(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.anonymousMatchMessageRelayService = AnonymousMatchMessageRelayService()

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return

        await self.anonymousMatchMessageRelayService.relayMessage(self.bot, message)


async def setup(bot):
    await bot.add_cog(AnonymousMatchMessageRelayEvent(bot))
