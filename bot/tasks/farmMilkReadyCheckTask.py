from datetime import datetime

import discord
from discord.ext import commands, tasks

from bot.config.channel import FARM_NOTIFICATION_CHANNEL_ID
from bot.config.database import getDbSession
from bot.config.emoji import FARM_GAME_EMOJI
from bot.helper.discordResolverHelper import resolveChannel
from bot.repository.farmCowShedRepository import FarmCowShedRepository
from bot.services.farm.farmCowMilkCollectService import FarmCowMilkCollectService


class FarmMilkReadyCheckTask(commands.Cog):
    MILK_READY_CHECK_INTERVAL_SECONDS = 180

    def __init__(self, bot):
        self.bot = bot
        self.checkFarmMilkReadyStatus.start()

    def cog_unload(self):
        self.checkFarmMilkReadyStatus.cancel()

    @tasks.loop(seconds=MILK_READY_CHECK_INTERVAL_SECONDS)
    async def checkFarmMilkReadyStatus(self):
        now = datetime.now()
        notificationSummaries = []

        with getDbSession() as session:
            farmCowShedRepository = FarmCowShedRepository(session)
            cowSheds = farmCowShedRepository.findMilkReadyShedsNeedNotification(
                now=now,
                milkCollectIntervalMinutes=FarmCowMilkCollectService.MILK_COLLECT_INTERVAL_MINUTES,
                hungryIntervalMinutes=FarmCowMilkCollectService.HUNGRY_INTERVAL_MINUTES,
            )

            for cowShed in cowSheds:
                farmCowShedRepository.markMilkReadyNotified(cowShed)
                member = self.getFarmOwnerMember(cowShed)

                if member is None or not member.is_allow_notifications:
                    continue

                notificationSummaries.append({
                    "userId": member.user_id,
                })

            session.commit()

        if cowSheds:
            print(f"Marked {len(cowSheds)} farm cow sheds as milk ready notified")

        await self.sendMilkReadyNotifications(notificationSummaries)

    @checkFarmMilkReadyStatus.before_loop
    async def beforeCheckFarmMilkReadyStatus(self):
        await self.bot.wait_until_ready()

    def getFarmOwnerMember(self, cowShed):
        if cowShed.farm is None:
            return None

        return cowShed.farm.member

    async def sendMilkReadyNotifications(self, notificationSummaries):
        if len(notificationSummaries) == 0:
            return

        notificationChannel = await resolveChannel(self.bot, FARM_NOTIFICATION_CHANNEL_ID, discord.TextChannel)

        if notificationChannel is None:
            return

        milkEmoji = FARM_GAME_EMOJI["item_milk"]

        for notificationSummary in notificationSummaries:
            await notificationChannel.send(
                content=(
                    f"<@{notificationSummary['userId']}>\n"
                    f"{milkEmoji} Sữa bò của bạn đã có thể thu hoạch."
                ),
                allowed_mentions=discord.AllowedMentions(
                    users=True,
                    roles=False,
                    everyone=False,
                ),
            )


async def setup(bot):
    await bot.add_cog(FarmMilkReadyCheckTask(bot))
