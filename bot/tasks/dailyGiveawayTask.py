from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from discord.ext import commands

from bot.services.giveaway.dailyGiveawayService import DailyGiveawayService


class DailyGiveawayTask(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.dailyGiveawayService = DailyGiveawayService()
        self.scheduler = AsyncIOScheduler(timezone="Asia/Ho_Chi_Minh")

        self.scheduler.add_job(
            self.runDailyGiveawayJob,
            CronTrigger(
                hour=8,
                minute=0,
                second=0,
                timezone="Asia/Ho_Chi_Minh",
            ),
            id="dailyGiveawayJob",
            replace_existing=True,
        )

        self.scheduler.start()

    async def runDailyGiveawayJob(self):
        try:
            await self.dailyGiveawayService.createDailyGiveaway(self.bot)
        except Exception as e:
            print(f"Daily giveaway job error: {e}")

    def cog_unload(self):
        if self.scheduler.running:
            self.scheduler.shutdown()


async def setup(bot):
    await bot.add_cog(DailyGiveawayTask(bot))
