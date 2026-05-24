from datetime import datetime

import discord
from discord.ext import commands, tasks

from bot.config.channel import FARM_NOTIFICATION_CHANNEL_ID
from bot.config.database import getDbSession
from bot.repository.farmCropAreaRepository import FarmCropAreaRepository


class FarmPestCheckTask(commands.Cog):
    PEST_CHECK_INTERVAL_SECONDS = 240
    PEST_THRESHOLD_MINUTES = 6

    def __init__(self, bot):
        self.bot = bot
        self.checkFarmPestStatus.start()

    def cog_unload(self):
        self.checkFarmPestStatus.cancel()

    @tasks.loop(seconds=PEST_CHECK_INTERVAL_SECONDS)
    async def checkFarmPestStatus(self):
        now = datetime.now()
        notificationUserIds = []

        with getDbSession() as session:
            farmCropAreaRepository = FarmCropAreaRepository(session)

            farmCropAreas = farmCropAreaRepository.findCropAreasNeedPestInfected(
                now=now,
                pestThresholdMinutes=self.PEST_THRESHOLD_MINUTES,
            )

            for farmCropArea in farmCropAreas:
                farmCropAreaRepository.markPestInfected(farmCropArea)

                member = self.getFarmOwnerMember(farmCropArea)

                if member is None:
                    continue

                if not member.is_allow_notifications:
                    continue

                notificationUserIds.append(member.user_id)

            session.commit()

        if farmCropAreas:
            print(f"Marked {len(farmCropAreas)} farm crop areas as pest infected")

        await self.sendPestNotification(notificationUserIds)

    @checkFarmPestStatus.before_loop
    async def beforeCheckFarmPestStatus(self):
        await self.bot.wait_until_ready()

    def getFarmOwnerMember(self, farmCropArea):
        if farmCropArea.farm is None:
            return None

        return farmCropArea.farm.member

    async def sendPestNotification(self, userIds):
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
                "Farm của bạn đã xuất hiện sâu bệnh <:bug:1498089075867914281>, hãy bắt sâu để không mất sản lượng nhé."
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
    await bot.add_cog(FarmPestCheckTask(bot))
