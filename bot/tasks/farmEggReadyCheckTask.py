from datetime import datetime

import discord
from discord.ext import commands, tasks

from bot.config.channel import FARM_NOTIFICATION_CHANNEL_ID
from bot.config.database import getDbSession
from bot.config.emoji import FARM_GAME_EMOJI
from bot.helper.discordResolverHelper import resolveChannel
from bot.repository.farmChickenCoopRepository import FarmChickenCoopRepository
from bot.services.farm.farmChickenEggCollectService import FarmChickenEggCollectService


class FarmEggReadyCheckTask(commands.Cog):
    EGG_READY_CHECK_INTERVAL_SECONDS = 180

    def __init__(self, bot):
        self.bot = bot
        self.checkFarmEggReadyStatus.start()

    def cog_unload(self):
        self.checkFarmEggReadyStatus.cancel()

    @tasks.loop(seconds=EGG_READY_CHECK_INTERVAL_SECONDS)
    async def checkFarmEggReadyStatus(self):
        now = datetime.now()
        notificationSummaries = []

        with getDbSession() as session:
            farmChickenCoopRepository = FarmChickenCoopRepository(session)
            chickenCoops = farmChickenCoopRepository.findEggReadyCoopsNeedNotification(
                now=now,
                eggCollectIntervalMinutes=FarmChickenEggCollectService.EGG_COLLECT_INTERVAL_MINUTES,
                hungryIntervalMinutes=FarmChickenEggCollectService.HUNGRY_INTERVAL_MINUTES,
            )

            for chickenCoop in chickenCoops:
                farmChickenCoopRepository.markEggReadyNotified(chickenCoop)
                member = self.getFarmOwnerMember(chickenCoop)

                if member is None or not member.is_allow_notifications:
                    continue

                notificationSummaries.append({
                    "userId": member.user_id,
                })

            session.commit()

        if chickenCoops:
            print(f"Marked {len(chickenCoops)} farm chicken coops as egg ready notified")

        await self.sendEggReadyNotifications(notificationSummaries)

    @checkFarmEggReadyStatus.before_loop
    async def beforeCheckFarmEggReadyStatus(self):
        await self.bot.wait_until_ready()

    def getFarmOwnerMember(self, chickenCoop):
        if chickenCoop.farm is None:
            return None

        return chickenCoop.farm.member

    async def sendEggReadyNotifications(self, notificationSummaries):
        if len(notificationSummaries) == 0:
            return

        notificationChannel = await resolveChannel(self.bot, FARM_NOTIFICATION_CHANNEL_ID, discord.TextChannel)

        if notificationChannel is None:
            return

        eggEmoji = FARM_GAME_EMOJI["item_egg"]

        for notificationSummary in notificationSummaries:
            await notificationChannel.send(
                content=(
                    f"<@{notificationSummary['userId']}>\n"
                    f"{eggEmoji} Trứng của bạn đã có thể thu hoạch."
                ),
                allowed_mentions=discord.AllowedMentions(
                    users=True,
                    roles=False,
                    everyone=False,
                ),
            )


async def setup(bot):
    await bot.add_cog(FarmEggReadyCheckTask(bot))
