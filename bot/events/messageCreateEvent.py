import discord
from discord.ext import commands

from bot.services.chat.chatCountService import ChatCountService
from bot.services.memberActivity.memberDailyActivityService import MemberDailyActivityService


class MessageCreateEvent(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.chatCountService = ChatCountService()
        self.memberDailyActivityService = MemberDailyActivityService()

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if not message.author.bot:
            self.chatCountService.addMessageCount(message)
            self.memberDailyActivityService.addChatActivity(message)


async def setup(bot):
    await bot.add_cog(MessageCreateEvent(bot))