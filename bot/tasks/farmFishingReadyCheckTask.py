from datetime import datetime

import discord
from discord.ext import commands, tasks

from bot.config.channel import FARM_NOTIFICATION_CHANNEL_ID
from bot.config.database import getDbSession
from bot.helper.discordResolverHelper import resolveChannel
from bot.repository.farmFishPondRepository import FarmFishPondRepository


class FarmFishingReadyCheckTask(commands.Cog):
    FISHING_READY_CHECK_INTERVAL_SECONDS = 180

    def __init__(self, bot):
        self.bot = bot
        self.checkFarmFishingReadyStatus.start()

    def cog_unload(self):
        self.checkFarmFishingReadyStatus.cancel()

    @tasks.loop(seconds=FISHING_READY_CHECK_INTERVAL_SECONDS)
    async def checkFarmFishingReadyStatus(self):
        notificationSummaries = []

        with getDbSession() as session:
            farmFishPondRepository = FarmFishPondRepository(session)
            farmFishPonds = farmFishPondRepository.findFishingReadyPondsNeedNotification(
                now=datetime.now(),
            )

            for farmFishPond in farmFishPonds:
                farmFishPondRepository.markFishingReadyNotified(farmFishPond)
                member = self.getFarmOwnerMember(farmFishPond)

                if member is None or not member.is_allow_notifications:
                    continue

                notificationSummaries.append({
                    "userId": member.user_id,
                })

            session.commit()

        if notificationSummaries:
            print(f"Marked {len(notificationSummaries)} farm fish ponds as fishing ready notified")

        await self.sendFishingReadyNotifications(notificationSummaries)

    @checkFarmFishingReadyStatus.before_loop
    async def beforeCheckFarmFishingReadyStatus(self):
        await self.bot.wait_until_ready()

    def getFarmOwnerMember(self, farmFishPond):
        if farmFishPond.farm is None:
            return None

        return farmFishPond.farm.member

    async def sendFishingReadyNotifications(self, notificationSummaries):
        if len(notificationSummaries) == 0:
            return

        notificationChannel = await resolveChannel(self.bot, FARM_NOTIFICATION_CHANNEL_ID, discord.TextChannel)

        if notificationChannel is None:
            return

        for notificationSummary in notificationSummaries:
            await notificationChannel.send(
                content=(
                    f"<@{notificationSummary['userId']}>\n"
                    "🎣 Bạn đã có thể câu cá lại."
                ),
                allowed_mentions=discord.AllowedMentions(
                    users=True,
                    roles=False,
                    everyone=False,
                ),
            )


async def setup(bot):
    await bot.add_cog(FarmFishingReadyCheckTask(bot))
