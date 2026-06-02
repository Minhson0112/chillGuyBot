import discord
from discord.ext import commands

from bot.config.config import CHILL_STATION_GUILD_ID
from bot.services.member.memberSyncService import MemberSyncService


class MemberUpdateEvent(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.memberSyncService = MemberSyncService()

    @commands.Cog.listener()
    async def on_member_update(self, before: discord.Member, after: discord.Member):
        if after.guild.id != CHILL_STATION_GUILD_ID:
            return

        if not self.hasMemberProfileChanged(before, after):
            return

        self.memberSyncService.syncDiscordMember(after)

    def hasMemberProfileChanged(self, before: discord.Member, after: discord.Member):
        return (
            before.global_name != after.global_name
            or before.name != after.name
            or before.nick != after.nick
        )


async def setup(bot):
    await bot.add_cog(MemberUpdateEvent(bot))
