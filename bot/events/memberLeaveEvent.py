import discord
from discord.ext import commands

from bot.services.member.memberLeaveService import MemberLeaveService


class MemberLeaveEvent(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.memberLeaveService = MemberLeaveService()

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        self.memberLeaveService.handleMemberLeave(member)


async def setup(bot):
    await bot.add_cog(MemberLeaveEvent(bot))