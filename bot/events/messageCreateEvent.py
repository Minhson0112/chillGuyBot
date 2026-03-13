import discord
from discord.ext import commands

from bot.services.chat.chatCountService import ChatCountService


class MessageCreateEvent(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.chatCountService = ChatCountService()

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if not message.author.bot:
            self.chatCountService.addMessageCount(message)

async def setup(bot):
    await bot.add_cog(MessageCreateEvent(bot))