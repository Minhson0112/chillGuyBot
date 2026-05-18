from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from discord.ext import commands

from bot.services.farm.farmTrainEventAutoService import FarmTrainEventAutoService


class FarmTrainEventAutoTask(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.farmTrainEventAutoService = FarmTrainEventAutoService()
        self.scheduler = AsyncIOScheduler(timezone="Asia/Ho_Chi_Minh")

        self.scheduler.add_job(
            self.runTrainEventJob,
            CronTrigger(
                hour="7,12,16,21",
                minute=0,
                second=0,
                timezone="Asia/Ho_Chi_Minh",
            ),
            id="farmTrainEventAutoJob",
            replace_existing=True,
        )

        self.scheduler.start()

    async def runTrainEventJob(self):
        try:
            self.farmTrainEventAutoService.runAutoTrainEvent()
            print(f"Farm train event auto job created")
        except Exception as e:
            print(f"Farm train event auto job error: {e}")

    def cog_unload(self):
        if self.scheduler.running:
            self.scheduler.shutdown()


async def setup(bot):
    await bot.add_cog(FarmTrainEventAutoTask(bot))