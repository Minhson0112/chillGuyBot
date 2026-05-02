from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from discord.ext import commands

from bot.services.memberActivity.monthlyTopChatRewardService import MonthlyTopChatRewardService


class MonthlyTopChatRewardTask(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.monthlyTopChatRewardService = MonthlyTopChatRewardService(bot)
        self.scheduler = AsyncIOScheduler(timezone="Asia/Ho_Chi_Minh")

        self.scheduler.add_job(
            self.runMonthlyTopChatRewardJob,
            CronTrigger(
                day="last",
                hour=12,
                minute=0,
                second=0,
                timezone="Asia/Ho_Chi_Minh",
            ),
            id="monthlyTopChatRewardJob",
            replace_existing=True,
        )

        self.scheduler.start()

    async def runMonthlyTopChatRewardJob(self):
        await self.monthlyTopChatRewardService.runMonthlyReward()

    def cog_unload(self):
        if self.scheduler.running:
            self.scheduler.shutdown()


async def setup(bot):
    await bot.add_cog(MonthlyTopChatRewardTask(bot))