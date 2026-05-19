from datetime import datetime

from discord.ext import commands, tasks

from bot.config.database import getDbSession
from bot.repository.farmCropAreaRepository import FarmCropAreaRepository


class FarmDryCheckTask(commands.Cog):
    DRY_CHECK_INTERVAL_SECONDS = 520
    DRY_THRESHOLD_MINUTES = 8

    def __init__(self, bot):
        self.bot = bot
        self.checkFarmDryStatus.start()

    def cog_unload(self):
        self.checkFarmDryStatus.cancel()

    @tasks.loop(seconds=DRY_CHECK_INTERVAL_SECONDS)
    async def checkFarmDryStatus(self):
        now = datetime.now()

        with getDbSession() as session:
            farmCropAreaRepository = FarmCropAreaRepository(session)

            farmCropAreas = farmCropAreaRepository.findCropAreasNeedDry(
                now=now,
                dryThresholdMinutes=self.DRY_THRESHOLD_MINUTES,
            )

            for farmCropArea in farmCropAreas:
                farmCropAreaRepository.markDry(farmCropArea)

            session.commit()

        if farmCropAreas:
            print(f"Marked {len(farmCropAreas)} farm crop areas as dry")

    @checkFarmDryStatus.before_loop
    async def beforeCheckFarmDryStatus(self):
        await self.bot.wait_until_ready()


async def setup(bot):
    await bot.add_cog(FarmDryCheckTask(bot))