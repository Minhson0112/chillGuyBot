from datetime import datetime

import discord
from discord.ext import commands, tasks

from bot.config.channel import FARM_NOTIFICATION_CHANNEL_ID
from bot.config.database import getDbSession
from bot.config.emoji import FARM_GAME_EMOJI
from bot.repository.farmKitchenRepository import FarmKitchenRepository


class FarmCookReadyCheckTask(commands.Cog):
    COOK_READY_CHECK_INTERVAL_SECONDS = 240

    def __init__(self, bot):
        self.bot = bot
        self.checkFarmCookReadyStatus.start()

    def cog_unload(self):
        self.checkFarmCookReadyStatus.cancel()

    @tasks.loop(seconds=COOK_READY_CHECK_INTERVAL_SECONDS)
    async def checkFarmCookReadyStatus(self):
        now = datetime.now()
        notificationSummaries = []

        with getDbSession() as session:
            farmKitchenRepository = FarmKitchenRepository(session)

            farmKitchens = farmKitchenRepository.findFinishedKitchensNeedNotification(
                now=now,
            )

            for farmKitchen in farmKitchens:
                farmKitchenRepository.markCookedReadyNotified(farmKitchen)

                member = self.getFarmOwnerMember(farmKitchen)

                if member is None:
                    continue

                if not member.is_allow_notifications:
                    continue

                recipe = farmKitchen.currentRecipe

                if recipe is None or recipe.resultItem is None:
                    continue

                notificationSummaries.append({
                    "userId": member.user_id,
                    "itemName": recipe.resultItem.name,
                    "itemEmoji": self.resolveItemEmoji(recipe.resultItem),
                })

            session.commit()

        if farmKitchens:
            print(f"Marked {len(farmKitchens)} farm kitchens as cooked ready notified")

        await self.sendCookReadyNotifications(notificationSummaries)

    @checkFarmCookReadyStatus.before_loop
    async def beforeCheckFarmCookReadyStatus(self):
        await self.bot.wait_until_ready()

    def getFarmOwnerMember(self, farmKitchen):
        if farmKitchen.farm is None:
            return None

        return farmKitchen.farm.member

    def resolveItemEmoji(self, item):
        return FARM_GAME_EMOJI.get(item.icon_image_key, "")

    async def sendCookReadyNotifications(self, notificationSummaries):
        if len(notificationSummaries) == 0:
            return

        notificationChannel = await self.resolveNotificationChannel()

        if notificationChannel is None:
            return

        for notificationSummary in notificationSummaries:
            itemText = (
                f"{notificationSummary['itemEmoji']} {notificationSummary['itemName']}"
            ).strip()

            await notificationChannel.send(
                content=(
                    f"<@{notificationSummary['userId']}>\n"
                    f"{itemText} của bạn đã nấu xong."
                ),
                allowed_mentions=discord.AllowedMentions(
                    users=True,
                    roles=False,
                    everyone=False,
                ),
            )

    async def resolveNotificationChannel(self):
        channel = self.bot.get_channel(FARM_NOTIFICATION_CHANNEL_ID)

        if channel is not None:
            return channel

        try:
            channel = await self.bot.fetch_channel(FARM_NOTIFICATION_CHANNEL_ID)
        except discord.NotFound:
            return None
        except discord.Forbidden:
            return None
        except discord.HTTPException:
            return None

        if not isinstance(channel, discord.TextChannel):
            return None

        return channel


async def setup(bot):
    await bot.add_cog(FarmCookReadyCheckTask(bot))
