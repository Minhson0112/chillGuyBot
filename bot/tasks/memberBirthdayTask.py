from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from discord.ext import commands

from bot.services.member.memberBirthdayAnnounceService import MemberBirthdayAnnounceService


class MemberBirthdayTask(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.memberBirthdayAnnounceService = MemberBirthdayAnnounceService(bot)
        self.scheduler = AsyncIOScheduler(timezone="Asia/Ho_Chi_Minh")
        self.scheduler.add_job(
            self.runBirthdayJob,
            CronTrigger(hour=12, minute=0),
            id="memberBirthdayJob",
            replace_existing=True,
        )
        self.scheduler.start()

    async def runBirthdayJob(self):
        await self.memberBirthdayAnnounceService.sendTodayBirthdayMessages()

    def cog_unload(self):
        if self.scheduler.running:
            self.scheduler.shutdown()

async def setup(bot):
    await bot.add_cog(MemberBirthdayTask(bot))