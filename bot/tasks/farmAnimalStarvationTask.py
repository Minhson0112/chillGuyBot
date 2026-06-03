import discord
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from discord.ext import commands

from bot.config.channel import FARM_NOTIFICATION_CHANNEL_ID
from bot.config.emoji import FARM_GAME_EMOJI
from bot.services.farm.farmAnimalStarvationService import FarmAnimalStarvationService


class FarmAnimalStarvationTask(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.farmAnimalStarvationService = FarmAnimalStarvationService()
        self.scheduler = AsyncIOScheduler(timezone="Asia/Ho_Chi_Minh")

        self.scheduler.add_job(
            self.runAnimalStarvationJob,
            CronTrigger(hour="*/8", minute=0),
            id="farmAnimalStarvationJob",
            replace_existing=True,
        )

        self.scheduler.start()

    async def runAnimalStarvationJob(self):
        result = self.farmAnimalStarvationService.removeStarvedAnimals()

        deadAnimalCount = result["deadChickenCount"] + result["deadCowCount"]

        if deadAnimalCount <= 0:
            return

        print(
            "Farm animal starvation completed: "
            f"deadChickenCount={result['deadChickenCount']}, "
            f"deadCowCount={result['deadCowCount']}"
        )

        await self.sendAnimalStarvationNotifications(result["notificationSummaries"])

    async def sendAnimalStarvationNotifications(self, notificationSummaries):
        if len(notificationSummaries) == 0:
            return

        notificationChannel = await self.resolveNotificationChannel()

        if notificationChannel is None:
            return

        for notificationSummary in notificationSummaries:
            await notificationChannel.send(
                content=self.buildAnimalStarvationNotificationMessage(notificationSummary),
                allowed_mentions=discord.AllowedMentions(
                    users=True,
                    roles=False,
                    everyone=False,
                ),
            )

    def buildAnimalStarvationNotificationMessage(self, notificationSummary):
        animalLines = []

        if notificationSummary["deadChickenCount"] > 0:
            chickenEmoji = FARM_GAME_EMOJI["item_chicken"]
            animalLines.append(
                f"- **{notificationSummary['deadChickenCount']}** {chickenEmoji} gà"
            )

        if notificationSummary["deadCowCount"] > 0:
            cowEmoji = FARM_GAME_EMOJI["item_cow"]
            animalLines.append(
                f"- **{notificationSummary['deadCowCount']}** {cowEmoji} bò"
            )

        return (
            f"<@{notificationSummary['userId']}>\n"
            "Vật nuôi trong farm của bạn đã bị bỏ đói quá lâu và chết:\n"
            f"{chr(10).join(animalLines)}\n"
            "Hãy nhớ cho vật nuôi ăn để tránh mất vật nuôi nhé."
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

    def cog_unload(self):
        if self.scheduler.running:
            self.scheduler.shutdown()


async def setup(bot):
    await bot.add_cog(FarmAnimalStarvationTask(bot))
