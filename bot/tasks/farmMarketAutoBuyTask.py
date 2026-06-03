from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
import discord
from discord.ext import commands

from bot.config.channel import FARM_NOTIFICATION_CHANNEL_ID
from bot.config.emoji import FARM_GAME_EMOJI
from bot.services.farm.farmMarketAutoBuyService import FarmMarketAutoBuyService


class FarmMarketAutoBuyTask(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.farmMarketAutoBuyService = FarmMarketAutoBuyService()
        self.scheduler = AsyncIOScheduler(timezone="Asia/Ho_Chi_Minh")

        self.scheduler.add_job(
            self.runAutoBuyJob,
            CronTrigger(hour="1,9,17", minute=0),
            id="farmMarketAutoBuyJob",
            replace_existing=True,
        )

        self.scheduler.start()

    async def runAutoBuyJob(self):
        if self.bot.user is None:
            print("Farm market auto buy skipped: bot user is None")
            return

        result = self.farmMarketAutoBuyService.autoBuyExpiredListings(
            botUserId=self.bot.user.id,
        )

        if not result["success"]:
            print(f"Farm market auto buy failed: {result['message']}")
            return

        print(
            "Farm market auto buy completed: "
            f"soldCount={result['soldCount']}, "
            f"totalPaid={result['totalPaid']}"
        )

        await self.sendAutoBuyNotifications(result.get("notificationSummaries", []))

    def cog_unload(self):
        if self.scheduler.running:
            self.scheduler.shutdown()

    async def sendAutoBuyNotifications(self, notificationSummaries):
        if len(notificationSummaries) == 0:
            return

        notificationChannel = await self.resolveNotificationChannel()

        if notificationChannel is None:
            return

        for notificationSummary in notificationSummaries:
            await notificationChannel.send(
                content=self.buildAutoBuyNotificationMessage(notificationSummary),
                allowed_mentions=discord.AllowedMentions(
                    users=True,
                    roles=False,
                    everyone=False,
                ),
            )

    def buildAutoBuyNotificationMessage(self, notificationSummary):
        chillCoinEmoji = FARM_GAME_EMOJI["chill_coin"]
        itemLines = [
            (
                f"- **{item['quantity']:,}** {item['itemText']}: "
                f"**{item['price']:,}** {chillCoinEmoji}"
            )
            for item in notificationSummary["items"]
        ]

        return (
            f"<@{notificationSummary['sellerUserId']}>\n"
            "Shop farm của bạn đã được Chill Guy mua các món sau:\n"
            f"{chr(10).join(itemLines)}\n"
            f"Tổng tiền nhận được: **{notificationSummary['totalPaid']:,}** {chillCoinEmoji}."
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
    await bot.add_cog(FarmMarketAutoBuyTask(bot))
