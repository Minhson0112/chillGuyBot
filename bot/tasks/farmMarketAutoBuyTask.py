from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from discord.ext import commands

from bot.services.farm.farmMarketAutoBuyService import FarmMarketAutoBuyService


class FarmMarketAutoBuyTask(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.farmMarketAutoBuyService = FarmMarketAutoBuyService()
        self.scheduler = AsyncIOScheduler(timezone="Asia/Ho_Chi_Minh")

        self.scheduler.add_job(
            self.runAutoBuyJob,
            CronTrigger(hour=0, minute=10),
            id="farmMarketAutoBuyJob",
            replace_existing=True,
        )

        self.scheduler.start()

    async def runAutoBuyJob(self):
        if self.bot.user is None:
            print("Farm market auto buy skipped: bot user is None")
            return

        result = self.farmMarketAutoBuyService.autoBuyExpiredListings(
            botUserId=self.bot.user.id,
        )

        if not result["success"]:
            print(f"Farm market auto buy failed: {result['message']}")
            return

        print(
            "Farm market auto buy completed: "
            f"soldCount={result['soldCount']}, "
            f"totalPaid={result['totalPaid']}"
        )

    def cog_unload(self):
        if self.scheduler.running:
            self.scheduler.shutdown()


async def setup(bot):
    await bot.add_cog(FarmMarketAutoBuyTask(bot))