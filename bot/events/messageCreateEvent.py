import discord
from discord.ext import commands

from bot.services.chat.chatCountService import ChatCountService
from bot.services.farm.dailyTaskChatCacheService import DailyTaskChatCacheService
from bot.services.memberActivity.memberDailyActivityService import MemberDailyActivityService


class MessageCreateEvent(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.chatCountService = ChatCountService()
        self.memberDailyActivityService = MemberDailyActivityService()
        self.dailyTaskChatCacheService = DailyTaskChatCacheService()

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return

        self.chatCountService.addMessageCount(message)
        self.memberDailyActivityService.addChatActivity(message)

        try:
            dailyTaskMessage = self.dailyTaskChatCacheService.addChatProgress(message)

            if dailyTaskMessage is not None:
                await message.reply(dailyTaskMessage)

        except Exception as e:
            print(f"Daily task chat cache progress error: {e}")


async def setup(bot):
    await bot.add_cog(MessageCreateEvent(bot))