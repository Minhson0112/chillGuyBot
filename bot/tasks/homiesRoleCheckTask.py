import asyncio

import discord
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from discord.ext import commands

from bot.helper.discordResolverHelper import resolveChannel
from bot.config.channel import BOT_NOTIFICATION_CHANNEL_ID, HOMIES_ROLE_CHANNEL_ID
from bot.config.roles import HOMIES_ROLE_ID
from bot.services.homies.homiesTagService import HomiesTagService


class HomiesRoleCheckTask(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.homiesTagService = HomiesTagService(bot)
        self.scheduler = AsyncIOScheduler(timezone="Asia/Ho_Chi_Minh")

        self.scheduler.add_job(
            self.runHomiesRoleCheckJob,
            CronTrigger(
                hour=0,
                minute=0,
                second=0,
                timezone="Asia/Ho_Chi_Minh",
            ),
            id="homiesRoleCheckJob",
            replace_existing=True,
        )

        self.scheduler.start()

    async def runHomiesRoleCheckJob(self):
        notificationChannel = await resolveChannel(self.bot, BOT_NOTIFICATION_CHANNEL_ID, discord.TextChannel)

        if notificationChannel is None:
            return

        guild = notificationChannel.guild
        homiesRole = guild.get_role(HOMIES_ROLE_ID)

        if homiesRole is None:
            await notificationChannel.send(
                embed=self.buildErrorEmbed(
                    title="Không tìm thấy role Homies",
                    description="Bot không tìm thấy role Homies trong server.",
                ),
                allowed_mentions=discord.AllowedMentions.none(),
            )
            return

        membersWithHomiesRole = list(homiesRole.members)

        if len(membersWithHomiesRole) == 0:
            return

        removedMembers = []

        for member in membersWithHomiesRole:
            if member.bot:
                continue

            hasChillStationTag = await self.homiesTagService.hasChillStationTagByUserId(
                userId=member.id,
            )

            if hasChillStationTag:
                await asyncio.sleep(0.2)
                continue

            removeResult = await self.removeHomiesRole(
                member=member,
                role=homiesRole,
            )

            if removeResult:
                removedMembers.append(member)

            await asyncio.sleep(0.2)

        if len(removedMembers) == 0:
            return

        await self.sendLostHomiesRoleMessages(
            notificationChannel=notificationChannel,
            removedMembers=removedMembers,
            homiesRole=homiesRole,
        )

    async def removeHomiesRole(
        self,
        member: discord.Member,
        role: discord.Role,
    ):
        if role not in member.roles:
            return False

        try:
            await member.remove_roles(
                role,
                reason="User no longer has Chill Station guild tag",
            )
            return True
        except discord.Forbidden:
            return False
        except discord.HTTPException:
            return False

    async def sendLostHomiesRoleMessages(
        self,
        notificationChannel: discord.TextChannel,
        removedMembers: list[discord.Member],
        homiesRole: discord.Role,
    ):
        chunkSize = 40

        for index in range(0, len(removedMembers), chunkSize):
            memberChunk = removedMembers[index:index + chunkSize]
            mentionText = " ".join([member.mention for member in memberChunk])

            await notificationChannel.send(
                content=mentionText,
                embed=self.buildLostHomiesRoleEmbed(homiesRole),
                allowed_mentions=discord.AllowedMentions(
                    users=True,
                    roles=False,
                    everyone=False,
                ),
            )

    def buildLostHomiesRoleEmbed(
        self,
        homiesRole: discord.Role,
    ):
        embed = discord.Embed(
            title="Role Homies đã bị gỡ",
            description=(
                f"Rất tiếc, bạn đã mất role {homiesRole.mention}.\n\n"
                f"Nếu muốn lấy lại role, hãy đáp ứng điều kiện và nhận lại role tại kênh <#{HOMIES_ROLE_CHANNEL_ID}>."
            ),
            color=discord.Color.orange(),
        )

        return embed

    def buildErrorEmbed(
        self,
        title: str,
        description: str,
    ):
        embed = discord.Embed(
            title=title,
            description=description,
            color=discord.Color.red(),
        )

        return embed

    def cog_unload(self):
        if self.scheduler.running:
            self.scheduler.shutdown()


async def setup(bot):
    await bot.add_cog(HomiesRoleCheckTask(bot))
