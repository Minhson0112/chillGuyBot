import discord
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from discord.ext import commands

from bot.config.config import CHILL_STATION_GUILD_ID
from bot.services.server.serverInviteSyncService import ServerInviteSyncService


class ServerInviteSyncTask(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.serverInviteSyncService = ServerInviteSyncService()
        self.scheduler = AsyncIOScheduler(timezone="Asia/Ho_Chi_Minh")

        self.scheduler.add_job(
            self.runServerInviteSyncJob,
            CronTrigger(
                hour="4,16",
                minute=0,
                second=0,
                timezone="Asia/Ho_Chi_Minh",
            ),
            id="serverInviteSyncJob",
            replace_existing=True,
            max_instances=1,
        )

        self.scheduler.start()

    async def runServerInviteSyncJob(self):
        await self.bot.wait_until_ready()

        try:
            guild = self.bot.get_guild(CHILL_STATION_GUILD_ID)

            if guild is None:
                guild = await self.bot.fetch_guild(CHILL_STATION_GUILD_ID)

            syncResult = await self.serverInviteSyncService.syncGuildInvites(guild)
            print(
                "Server invite sync job fetched "
                f"{syncResult['fetchedCount']} invites, "
                f"created {syncResult['createdCount']}, "
                f"updated {syncResult['updatedCount']}, "
                f"unchanged {syncResult['unchangedCount']}"
            )
        except discord.Forbidden:
            print("Server invite sync job error: bot does not have permission to fetch guild invites")
        except discord.HTTPException as e:
            print(f"Server invite sync job discord error: {e}")
        except Exception as e:
            print(f"Server invite sync job error: {e}")

    def cog_unload(self):
        if self.scheduler.running:
            self.scheduler.shutdown()


async def setup(bot):
    await bot.add_cog(ServerInviteSyncTask(bot))
