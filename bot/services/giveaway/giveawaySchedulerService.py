import asyncio
from datetime import timedelta, timezone

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.date import DateTrigger

from bot.config.database import getDbSession
from bot.repository.giveawayRepository import GiveawayRepository
from bot.services.giveaway.giveawayDrawService import GiveawayDrawService


class GiveawaySchedulerService:
    GMT7 = timezone(timedelta(hours=7))
    JOB_ID_PREFIX = "giveaway_draw"

    def __init__(self):
        self.bot = None
        self.scheduler = AsyncIOScheduler(timezone=self.GMT7)
        self.scheduledGiveawayIds = set()
        self.runningGiveawayIds = set()
        self.giveawayDrawService = GiveawayDrawService()

    def start(self, bot):
        self.bot = bot

        if not self.scheduler.running:
            self.scheduler.start()

        self.reloadSchedule()

    def shutdown(self):
        if self.scheduler.running:
            self.scheduler.shutdown()

        self.scheduledGiveawayIds.clear()
        self.runningGiveawayIds.clear()

    def reloadSchedule(self):
        if self.bot is None:
            return

        self.clearScheduledJobs()

        with getDbSession() as session:
            giveawayRepository = GiveawayRepository(session)
            giveaways = giveawayRepository.findActiveGiveawaysWithMessage()

            for giveaway in giveaways:
                self.scheduleGiveaway(giveaway)

        print(f"✅ Đã load giveaway schedule cache: {len(self.scheduledGiveawayIds)} job")

    def clearScheduledJobs(self):
        for job in self.scheduler.get_jobs():
            if job.id.startswith(f"{self.JOB_ID_PREFIX}:"):
                job.remove()

        self.scheduledGiveawayIds.clear()

    def scheduleGiveaway(self, giveaway):
        if giveaway.id in self.runningGiveawayIds:
            return

        runDate = giveaway.draw_at.replace(tzinfo=self.GMT7)

        if runDate <= self.getNow():
            self.runningGiveawayIds.add(giveaway.id)
            asyncio.create_task(self.runGiveawayJob(giveaway.id))
            return

        self.scheduler.add_job(
            self.runGiveawayJob,
            DateTrigger(run_date=runDate),
            args=[giveaway.id],
            id=self.buildJobId(giveaway.id),
            replace_existing=True,
        )
        self.scheduledGiveawayIds.add(giveaway.id)

    async def runGiveawayJob(self, giveawayId: int):
        self.scheduledGiveawayIds.discard(giveawayId)
        self.runningGiveawayIds.add(giveawayId)

        try:
            await self.giveawayDrawService.sendGiveawayResult(
                bot=self.bot,
                giveawayId=giveawayId,
            )
        finally:
            self.runningGiveawayIds.discard(giveawayId)

    def buildJobId(self, giveawayId: int):
        return f"{self.JOB_ID_PREFIX}:{giveawayId}"

    def getNow(self):
        from datetime import datetime

        return datetime.now(self.GMT7)


giveawaySchedulerService = GiveawaySchedulerService()
