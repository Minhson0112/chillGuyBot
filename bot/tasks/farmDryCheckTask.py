from datetime import datetime

import discord
from discord.ext import commands, tasks

from bot.config.channel import FARM_NOTIFICATION_CHANNEL_ID
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
        notificationUserIds = []

        with getDbSession() as session:
            farmCropAreaRepository = FarmCropAreaRepository(session)

            farmCropAreas = farmCropAreaRepository.findCropAreasNeedDry(
                now=now,
                dryThresholdMinutes=self.DRY_THRESHOLD_MINUTES,
            )

            for farmCropArea in farmCropAreas:
                farmCropAreaRepository.markDry(farmCropArea)

                member = self.getFarmOwnerMember(farmCropArea)

                if member is None:
                    continue

                if not member.is_allow_notifications:
                    continue

                notificationUserIds.append(member.user_id)

            session.commit()

        if farmCropAreas:
            print(f"Marked {len(farmCropAreas)} farm crop areas as dry")

        await self.sendDryNotification(notificationUserIds)

    @checkFarmDryStatus.before_loop
    async def beforeCheckFarmDryStatus(self):
        await self.bot.wait_until_ready()

    def getFarmOwnerMember(self, farmCropArea):
        if farmCropArea.farm is None:
            return None

        return farmCropArea.farm.member

    async def sendDryNotification(self, userIds):
        uniqueUserIds = list(dict.fromkeys(userIds))

        if len(uniqueUserIds) == 0:
            return

        notificationChannel = await self.resolveNotificationChannel()

        if notificationChannel is None:
            return

        mentionText = "".join([f"<@{userId}>" for userId in uniqueUserIds])

        await notificationChannel.send(
            content=(
                f"{mentionText}\n"
                "Đất trong farm của bạn đã bị khô, hãy tưới nước <:watering:1501945506018885743> để không mất sản lượng nhé."
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
    await bot.add_cog(FarmDryCheckTask(bot))
