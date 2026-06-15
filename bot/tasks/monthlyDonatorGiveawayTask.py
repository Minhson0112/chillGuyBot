from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from discord.ext import commands

from bot.services.giveaway.monthlyDonatorGiveawayService import MonthlyDonatorGiveawayService


class MonthlyDonatorGiveawayTask(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.monthlyDonatorGiveawayService = MonthlyDonatorGiveawayService()
        self.scheduler = AsyncIOScheduler(timezone="Asia/Ho_Chi_Minh")

        self.scheduler.add_job(
            self.runMonthlyDonatorGiveawayJob,
            CronTrigger(
                day="last",
                hour=8,
                minute=30,
                second=0,
                timezone="Asia/Ho_Chi_Minh",
            ),
            id="monthlyDonatorGiveawayJob",
            replace_existing=True,
            max_instances=1,
        )

        self.scheduler.start()

    async def runMonthlyDonatorGiveawayJob(self):
        try:
            await self.monthlyDonatorGiveawayService.createMonthlyDonatorGiveaway(self.bot)
        except Exception as e:
            print(f"Monthly donator giveaway job error: {e}")

    def cog_unload(self):
        if self.scheduler.running:
            self.scheduler.shutdown()


async def setup(bot):
    await bot.add_cog(MonthlyDonatorGiveawayTask(bot))
