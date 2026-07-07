from datetime import datetime

from discord.ext import commands, tasks

from bot.cache.coupleVoiceScanCache import lastCoupleVoiceScanAt
from bot.services.serverItem.coupleVoiceActivityService import CoupleVoiceActivityService


class CoupleVoiceActivityTask(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.coupleVoiceActivityService = CoupleVoiceActivityService()
        self.trackCoupleVoiceActivity.start()

    def cog_unload(self):
        self.trackCoupleVoiceActivity.cancel()

    @tasks.loop(minutes=1)
    async def trackCoupleVoiceActivity(self):
        now = datetime.now(self.coupleVoiceActivityService.gmt7)
        previousScanAt = lastCoupleVoiceScanAt["value"]

        self.coupleVoiceActivityService.refreshActiveCoupleCache()

        if previousScanAt is None:
            lastCoupleVoiceScanAt["value"] = now
            return

        sameVoiceCoupleIds = self.coupleVoiceActivityService.collectSameVoiceCoupleIds(
            self.bot.guilds,
        )
        self.coupleVoiceActivityService.addVoiceSecondsToCouples(
            coupleIds=sameVoiceCoupleIds,
            startedAt=previousScanAt,
            endedAt=now,
        )
        lastCoupleVoiceScanAt["value"] = now

    @trackCoupleVoiceActivity.before_loop
    async def beforeTrackCoupleVoiceActivity(self):
        await self.bot.wait_until_ready()


async def setup(bot):
    await bot.add_cog(CoupleVoiceActivityTask(bot))
