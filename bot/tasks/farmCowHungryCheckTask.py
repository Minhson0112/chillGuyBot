from datetime import datetime

import discord
from discord.ext import commands, tasks

from bot.config.channel import FARM_NOTIFICATION_CHANNEL_ID
from bot.config.database import getDbSession
from bot.config.emoji import FARM_GAME_EMOJI
from bot.helper.discordResolverHelper import resolveChannel
from bot.repository.farmCowShedRepository import FarmCowShedRepository
from bot.services.farm.farmCowFeedService import FarmCowFeedService


class FarmCowHungryCheckTask(commands.Cog):
    COW_HUNGRY_CHECK_INTERVAL_SECONDS = 180

    def __init__(self, bot):
        self.bot = bot
        self.checkFarmCowHungryStatus.start()

    def cog_unload(self):
        self.checkFarmCowHungryStatus.cancel()

    @tasks.loop(seconds=COW_HUNGRY_CHECK_INTERVAL_SECONDS)
    async def checkFarmCowHungryStatus(self):
        notificationSummaries = []

        with getDbSession() as session:
            farmCowShedRepository = FarmCowShedRepository(session)
            cowSheds = farmCowShedRepository.findHungryCowShedsNeedNotification(
                now=datetime.now(),
                hungryIntervalMinutes=FarmCowFeedService.HUNGRY_INTERVAL_MINUTES,
            )

            for cowShed in cowSheds:
                farmCowShedRepository.markHungryNotified(cowShed)
                member = self.getFarmOwnerMember(cowShed)

                if member is None or not member.is_allow_notifications:
                    continue

                notificationSummaries.append({
                    "userId": member.user_id,
                })

            session.commit()

        if cowSheds:
            print(f"Marked {len(cowSheds)} farm cow sheds as hungry notified")

        await self.sendCowHungryNotifications(notificationSummaries)

    @checkFarmCowHungryStatus.before_loop
    async def beforeCheckFarmCowHungryStatus(self):
        await self.bot.wait_until_ready()

    def getFarmOwnerMember(self, cowShed):
        if cowShed.farm is None:
            return None

        return cowShed.farm.member

    async def sendCowHungryNotifications(self, notificationSummaries):
        if len(notificationSummaries) == 0:
            return

        notificationChannel = await resolveChannel(self.bot, FARM_NOTIFICATION_CHANNEL_ID, discord.TextChannel)

        if notificationChannel is None:
            return

        cowEmoji = FARM_GAME_EMOJI["item_cow"]

        for notificationSummary in notificationSummaries:
            await notificationChannel.send(
                content=(
                    f"<@{notificationSummary['userId']}>\n"
                    f"{cowEmoji} Bò của bạn đang đói. Hãy cho bò ăn."
                ),
                allowed_mentions=discord.AllowedMentions(
                    users=True,
                    roles=False,
                    everyone=False,
                ),
            )


async def setup(bot):
    await bot.add_cog(FarmCowHungryCheckTask(bot))
