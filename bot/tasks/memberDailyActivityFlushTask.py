from discord.ext import commands, tasks

from bot.cache.memberDailyActivityCache import memberDailyActivityCache
from bot.config.database import getDbSession
from bot.repository.memberDailyActivityRepository import MemberDailyActivityRepository


class MemberDailyActivityFlushTask(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.flushMemberDailyActivity.start()

    def cog_unload(self):
        self.flushMemberDailyActivity.cancel()

    @tasks.loop(minutes=1)
    async def flushMemberDailyActivity(self):
        if not memberDailyActivityCache:
            return

        pendingCache = dict(memberDailyActivityCache)
        memberDailyActivityCache.clear()

        try:
            with getDbSession() as session:
                memberDailyActivityRepository = MemberDailyActivityRepository(session)

                for cacheKey, counts in pendingCache.items():
                    userId, activityDate = cacheKey

                    memberDailyActivityRepository.incrementDailyActivity(
                        userId,
                        activityDate,
                        counts["total_chat_count"],
                        counts["level_chat_count"],
                        counts["voice_seconds"],
                    )

                session.commit()

        except Exception:
            for cacheKey, counts in pendingCache.items():
                if cacheKey not in memberDailyActivityCache:
                    memberDailyActivityCache[cacheKey] = {
                        "total_chat_count": 0,
                        "level_chat_count": 0,
                        "voice_seconds": 0,
                    }

                memberDailyActivityCache[cacheKey]["total_chat_count"] += counts["total_chat_count"]
                memberDailyActivityCache[cacheKey]["level_chat_count"] += counts["level_chat_count"]
                memberDailyActivityCache[cacheKey]["voice_seconds"] += counts["voice_seconds"]

            raise

    @flushMemberDailyActivity.before_loop
    async def beforeFlushMemberDailyActivity(self):
        await self.bot.wait_until_ready()


async def setup(bot):
    await bot.add_cog(MemberDailyActivityFlushTask(bot))