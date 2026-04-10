import discord
from discord.ext import commands

from bot.services.member.memberJoinService import MemberJoinService
from bot.services.achievement.memberAchievementService import MemberAchievementService


class MemberJoinEvent(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.memberJoinService = MemberJoinService()
        self.memberAchievementService = MemberAchievementService()

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        self.memberJoinService.handleMemberJoin(member)
        await self.memberAchievementService.handleMemberMilestone(member.guild)


async def setup(bot):
    await bot.add_cog(MemberJoinEvent(bot))