from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from discord.ext import commands

from bot.config.config import CHILL_STATION_GUILD_ID
from bot.services.donate.monthlyDonatorRoleService import MonthlyDonatorRoleService


class MonthlyDonatorRoleCleanupTask(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.monthlyDonatorRoleService = MonthlyDonatorRoleService()
        self.scheduler = AsyncIOScheduler(timezone="Asia/Ho_Chi_Minh")

        self.scheduler.add_job(
            self.runMonthlyDonatorRoleCleanupJob,
            CronTrigger(
                day=3,
                hour=0,
                minute=15,
                second=0,
                timezone="Asia/Ho_Chi_Minh",
            ),
            id="monthlyDonatorRoleCleanupJob",
            replace_existing=True,
            max_instances=1,
        )

        self.scheduler.start()

    async def runMonthlyDonatorRoleCleanupJob(self):
        await self.bot.wait_until_ready()

        guild = self.bot.get_guild(CHILL_STATION_GUILD_ID)

        if guild is None:
            guild = await self.bot.fetch_guild(CHILL_STATION_GUILD_ID)

        await self.monthlyDonatorRoleService.deletePreviousMonthRole(guild)

    def cog_unload(self):
        if self.scheduler.running:
            self.scheduler.shutdown()


async def setup(bot):
    await bot.add_cog(MonthlyDonatorRoleCleanupTask(bot))
