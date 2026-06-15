import discord
from discord.ext import commands

from bot.config.config import CHILL_STATION_GUILD_ID
from bot.config.roles import DEFAULT_BOOSTER_ROLE_ID
from bot.services.booster.boosterCustomRoleExpireService import BoosterCustomRoleExpireService
from bot.services.member.memberSyncService import MemberSyncService


class MemberUpdateEvent(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.memberSyncService = MemberSyncService()
        self.boosterCustomRoleExpireService = BoosterCustomRoleExpireService()

    @commands.Cog.listener()
    async def on_member_update(self, before: discord.Member, after: discord.Member):
        if after.guild.id != CHILL_STATION_GUILD_ID:
            return

        await self.handleMemberProfileChanged(before, after)
        await self.handleBoosterExpired(before, after)

    async def handleMemberProfileChanged(self, before: discord.Member, after: discord.Member):
        if not self.hasMemberProfileChanged(before, after):
            return

        self.memberSyncService.syncDiscordMember(after)

    async def handleBoosterExpired(self, before: discord.Member, after: discord.Member):
        if not self.hasMemberBoosterExpired(before, after):
            return

        await self.boosterCustomRoleExpireService.handleBoosterExpired(self.bot, after)

    def hasMemberProfileChanged(self, before: discord.Member, after: discord.Member):
        return (
            before.global_name != after.global_name
            or before.name != after.name
            or before.nick != after.nick
        )

    def hasMemberBoosterExpired(self, before: discord.Member, after: discord.Member):
        return (
            before.premium_since != after.premium_since
            and before.premium_since is not None
            and after.premium_since is None
            and not self.hasDefaultBoosterRole(after)
        )

    def hasDefaultBoosterRole(self, member: discord.Member):
        return any(role.id == DEFAULT_BOOSTER_ROLE_ID for role in member.roles)


async def setup(bot):
    await bot.add_cog(MemberUpdateEvent(bot))
