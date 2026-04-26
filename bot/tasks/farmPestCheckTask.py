from datetime import datetime

from discord.ext import commands, tasks

from bot.config.database import getDbSession
from bot.repository.farmCropAreaRepository import FarmCropAreaRepository


class FarmPestCheckTask(commands.Cog):
    PEST_CHECK_INTERVAL_SECONDS = 600
    PEST_THRESHOLD_MINUTES = 10

    def __init__(self, bot):
        self.bot = bot
        self.checkFarmPestStatus.start()

    def cog_unload(self):
        self.checkFarmPestStatus.cancel()

    @tasks.loop(seconds=PEST_CHECK_INTERVAL_SECONDS)
    async def checkFarmPestStatus(self):
        now = datetime.now()

        with getDbSession() as session:
            farmCropAreaRepository = FarmCropAreaRepository(session)

            farmCropAreas = farmCropAreaRepository.findCropAreasNeedPestInfected(
                now=now,
                pestThresholdMinutes=self.PEST_THRESHOLD_MINUTES,
            )

            for farmCropArea in farmCropAreas:
                farmCropAreaRepository.markPestInfected(farmCropArea)

            session.commit()

        if farmCropAreas:
            print(f"Marked {len(farmCropAreas)} farm crop areas as pest infected")

    @checkFarmPestStatus.before_loop
    async def beforeCheckFarmPestStatus(self):
        await self.bot.wait_until_ready()


async def setup(bot):
    await bot.add_cog(FarmPestCheckTask(bot))