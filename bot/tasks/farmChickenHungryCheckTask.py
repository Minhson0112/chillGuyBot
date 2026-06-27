from datetime import datetime

import discord
from discord.ext import commands, tasks

from bot.config.channel import FARM_NOTIFICATION_CHANNEL_ID
from bot.config.database import getDbSession
from bot.config.emoji import FARM_GAME_EMOJI
from bot.helper.discordResolverHelper import resolveChannel
from bot.repository.farmChickenCoopRepository import FarmChickenCoopRepository
from bot.services.farm.farmChickenFeedService import FarmChickenFeedService


class FarmChickenHungryCheckTask(commands.Cog):
    CHICKEN_HUNGRY_CHECK_INTERVAL_SECONDS = 180

    def __init__(self, bot):
        self.bot = bot
        self.checkFarmChickenHungryStatus.start()

    def cog_unload(self):
        self.checkFarmChickenHungryStatus.cancel()

    @tasks.loop(seconds=CHICKEN_HUNGRY_CHECK_INTERVAL_SECONDS)
    async def checkFarmChickenHungryStatus(self):
        notificationSummaries = []

        with getDbSession() as session:
            farmChickenCoopRepository = FarmChickenCoopRepository(session)
            chickenCoops = farmChickenCoopRepository.findHungryChickenCoopsNeedNotification(
                now=datetime.now(),
                hungryIntervalMinutes=FarmChickenFeedService.HUNGRY_INTERVAL_MINUTES,
            )

            for chickenCoop in chickenCoops:
                farmChickenCoopRepository.markHungryNotified(chickenCoop)
                member = self.getFarmOwnerMember(chickenCoop)

                if member is None or not member.is_allow_notifications:
                    continue

                notificationSummaries.append({
                    "userId": member.user_id,
                })

            session.commit()

        if chickenCoops:
            print(f"Marked {len(chickenCoops)} farm chicken coops as hungry notified")

        await self.sendChickenHungryNotifications(notificationSummaries)

    @checkFarmChickenHungryStatus.before_loop
    async def beforeCheckFarmChickenHungryStatus(self):
        await self.bot.wait_until_ready()

    def getFarmOwnerMember(self, chickenCoop):
        if chickenCoop.farm is None:
            return None

        return chickenCoop.farm.member

    async def sendChickenHungryNotifications(self, notificationSummaries):
        if len(notificationSummaries) == 0:
            return

        notificationChannel = await resolveChannel(self.bot, FARM_NOTIFICATION_CHANNEL_ID, discord.TextChannel)

        if notificationChannel is None:
            return

        chickenEmoji = FARM_GAME_EMOJI["item_chicken"]

        for notificationSummary in notificationSummaries:
            await notificationChannel.send(
                content=(
                    f"<@{notificationSummary['userId']}>\n"
                    f"{chickenEmoji} Gà của bạn đang đói. Hãy cho gà ăn."
                ),
                allowed_mentions=discord.AllowedMentions(
                    users=True,
                    roles=False,
                    everyone=False,
                ),
            )


async def setup(bot):
    await bot.add_cog(FarmChickenHungryCheckTask(bot))
