import discord
from discord.ext import commands

from bot.services.anonymousMatch.anonymousMatchStopService import AnonymousMatchStopService
from bot.services.member.memberLeaveService import MemberLeaveService


class MemberLeaveEvent(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.memberLeaveService = MemberLeaveService()
        self.anonymousMatchStopService = AnonymousMatchStopService()

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        await self.memberLeaveService.handleMemberLeave(self.bot, member)
        await self.anonymousMatchStopService.endMatchByMemberLeave(self.bot, member.id)


async def setup(bot):
    await bot.add_cog(MemberLeaveEvent(bot))
