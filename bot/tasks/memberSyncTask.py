from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from discord.ext import commands

from bot.config.config import CHILL_STATION_GUILD_ID
from bot.services.member.memberSyncService import MemberSyncService


class MemberSyncTask(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.memberSyncService = MemberSyncService()
        self.scheduler = AsyncIOScheduler(timezone="Asia/Ho_Chi_Minh")

        self.scheduler.add_job(
            self.runMemberSyncJob,
            CronTrigger(
                hour=3,
                minute=0,
                second=0,
                timezone="Asia/Ho_Chi_Minh",
            ),
            id="memberSyncJob",
            replace_existing=True,
            max_instances=1,
        )

        self.scheduler.start()

    async def runMemberSyncJob(self):
        await self.bot.wait_until_ready()

        try:
            guild = self.bot.get_guild(CHILL_STATION_GUILD_ID)
            if guild is None:
                guild = await self.bot.fetch_guild(CHILL_STATION_GUILD_ID)

            syncedCount = await self.memberSyncService.syncGuildMembers(guild)
            print(f"Member sync job updated {syncedCount} members")
        except Exception as e:
            print(f"Member sync job error: {e}")

    def cog_unload(self):
        if self.scheduler.running:
            self.scheduler.shutdown()


async def setup(bot):
    await bot.add_cog(MemberSyncTask(bot))
