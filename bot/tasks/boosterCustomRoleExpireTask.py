import asyncio

import discord
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from discord.ext import commands

from bot.config.config import CHILL_STATION_GUILD_ID
from bot.config.database import getDbSession
from bot.config.roles import DEFAULT_BOOSTER_ROLE_ID
from bot.repository.boosterCustomRoleRepository import BoosterCustomRoleRepository
from bot.services.booster.boosterCustomRoleExpireService import BoosterCustomRoleExpireService


class BoosterCustomRoleExpireTask(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.boosterCustomRoleExpireService = BoosterCustomRoleExpireService()
        self.scheduler = AsyncIOScheduler(timezone="Asia/Ho_Chi_Minh")

        self.scheduler.add_job(
            self.runBoosterCustomRoleExpireJob,
            CronTrigger(
                hour=7,
                minute=0,
                second=0,
                timezone="Asia/Ho_Chi_Minh",
            ),
            id="boosterCustomRoleExpireJob",
            replace_existing=True,
            max_instances=1,
        )

        self.scheduler.start()

    async def runBoosterCustomRoleExpireJob(self):
        await self.bot.wait_until_ready()

        try:
            guild = self.bot.get_guild(CHILL_STATION_GUILD_ID)

            if guild is None:
                guild = await self.bot.fetch_guild(CHILL_STATION_GUILD_ID)

            activeTargetUserIds = self.findActiveTargetUserIds()

            for userId in activeTargetUserIds:
                member = await self.resolveGuildMember(guild, userId)

                if member is None:
                    continue

                if not self.hasExpiredBooster(member):
                    continue

                await self.boosterCustomRoleExpireService.handleBoosterExpired(
                    bot=self.bot,
                    member=member,
                )
                await asyncio.sleep(0.2)
        except Exception as e:
            print(f"Booster custom role expire job error: {e}")

    def findActiveTargetUserIds(self):
        with getDbSession() as session:
            boosterCustomRoleRepository = BoosterCustomRoleRepository(session)
            return boosterCustomRoleRepository.findActiveTargetUserIds()

    async def resolveGuildMember(self, guild: discord.Guild, userId: int):
        member = guild.get_member(userId)

        if member is not None:
            return member

        try:
            return await guild.fetch_member(userId)
        except discord.NotFound:
            return None
        except discord.HTTPException:
            return None

    def hasExpiredBooster(self, member: discord.Member):
        return (
            member.premium_since is None
            and not self.hasDefaultBoosterRole(member)
        )

    def hasDefaultBoosterRole(self, member: discord.Member):
        return any(role.id == DEFAULT_BOOSTER_ROLE_ID for role in member.roles)

    def cog_unload(self):
        if self.scheduler.running:
            self.scheduler.shutdown()


async def setup(bot):
    await bot.add_cog(BoosterCustomRoleExpireTask(bot))
