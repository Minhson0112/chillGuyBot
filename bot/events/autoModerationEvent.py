import discord
from discord.ext import commands

from bot.services.moderation.autoModerationService import AutoModerationService


class AutoModerationEvent(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.autoModerationService = AutoModerationService()

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        await self.autoModerationService.handleMessage(self.bot, message)

async def setup(bot):
    await bot.add_cog(AutoModerationEvent(bot))