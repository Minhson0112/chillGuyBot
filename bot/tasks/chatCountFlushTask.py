from discord.ext import commands, tasks

from bot.cache.chatCountCache import chatCountCache
from bot.config.database import getDbSession
from bot.repository.chatRepository import ChatRepository


class ChatCountFlushTask(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.flushChatCount.start()

    def cog_unload(self):
        self.flushChatCount.cancel()

    @tasks.loop(seconds=30)
    async def flushChatCount(self):
        global chatCountCache

        if not chatCountCache:
            return

        pendingCache = dict(chatCountCache)
        chatCountCache.clear()

        with getDbSession() as session:
            chatRepository = ChatRepository(session)

            for userId, counts in pendingCache.items():
                chatRepository.incrementChatCount(
                    userId,
                    counts["total_chat_count"],
                    counts["level_chat_count"],
                )

            session.commit()

    @flushChatCount.before_loop
    async def beforeFlushChatCount(self):
        await self.bot.wait_until_ready()


async def setup(bot):
    await bot.add_cog(ChatCountFlushTask(bot))