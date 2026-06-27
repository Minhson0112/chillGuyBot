from datetime import datetime

import discord
from discord.ext import commands, tasks

from bot.helper.discordResolverHelper import resolveChannel
from bot.config.channel import FARM_NOTIFICATION_CHANNEL_ID
from bot.config.database import getDbSession
from bot.helper.farmItemHelper import getItemEmoji
from bot.repository.farmCropAreaRepository import FarmCropAreaRepository


class FarmHarvestReadyCheckTask(commands.Cog):
    HARVEST_READY_CHECK_INTERVAL_SECONDS = 180

    def __init__(self, bot):
        self.bot = bot
        self.checkFarmHarvestReadyStatus.start()

    def cog_unload(self):
        self.checkFarmHarvestReadyStatus.cancel()

    @tasks.loop(seconds=HARVEST_READY_CHECK_INTERVAL_SECONDS)
    async def checkFarmHarvestReadyStatus(self):
        now = datetime.now()
        notificationSummaries = []

        with getDbSession() as session:
            farmCropAreaRepository = FarmCropAreaRepository(session)

            farmCropAreas = farmCropAreaRepository.findHarvestableCropAreasNeedNotification(
                now=now,
            )

            for farmCropArea in farmCropAreas:
                farmCropAreaRepository.markHarvestReadyNotified(farmCropArea)

                member = self.getFarmOwnerMember(farmCropArea)

                if member is None:
                    continue

                if not member.is_allow_notifications:
                    continue

                crop = farmCropArea.crop

                if crop is None:
                    continue

                notificationSummaries.append({
                    "userId": member.user_id,
                    "cropName": crop.name,
                    "cropEmoji": getItemEmoji(crop.cropItem, ""),
                })

            session.commit()

        if farmCropAreas:
            print(f"Marked {len(farmCropAreas)} farm crop areas as harvest ready notified")

        await self.sendHarvestReadyNotifications(notificationSummaries)

    @checkFarmHarvestReadyStatus.before_loop
    async def beforeCheckFarmHarvestReadyStatus(self):
        await self.bot.wait_until_ready()

    def getFarmOwnerMember(self, farmCropArea):
        if farmCropArea.farm is None:
            return None

        return farmCropArea.farm.member

    async def sendHarvestReadyNotifications(self, notificationSummaries):
        if len(notificationSummaries) == 0:
            return

        notificationChannel = await resolveChannel(self.bot, FARM_NOTIFICATION_CHANNEL_ID, discord.TextChannel)

        if notificationChannel is None:
            return

        for notificationSummary in notificationSummaries:
            cropText = (
                f"{notificationSummary['cropEmoji']} {notificationSummary['cropName']}"
            ).strip()

            await notificationChannel.send(
                content=(
                    f"<@{notificationSummary['userId']}>\n"
                    f"{cropText} của bạn đã sẵn sàng thu hoạch."
                ),
                allowed_mentions=discord.AllowedMentions(
                    users=True,
                    roles=False,
                    everyone=False,
                ),
            )


async def setup(bot):
    await bot.add_cog(FarmHarvestReadyCheckTask(bot))
