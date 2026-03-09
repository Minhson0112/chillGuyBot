import discord
from discord.ext import commands

from bot.services.member.memberJoinService import MemberJoinService


class MemberJoinEvent(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.memberJoinService = MemberJoinService()

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        self.memberJoinService.handleMemberJoin(member)


async def setup(bot):
    await bot.add_cog(MemberJoinEvent(bot))