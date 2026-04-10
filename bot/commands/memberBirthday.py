from discord.ext import commands

from bot.config.config import BIRTHDAY_CHANNEL_ID
from bot.services.member.memberBirthdayService import MemberBirthdayService


class MemberBirthday(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.memberBirthdayService = MemberBirthdayService()

    @commands.command(name="sn")
    async def setBirthday(self, ctx, birthdayText: str = None):
        if ctx.channel.id != BIRTHDAY_CHANNEL_ID:
            return

        if birthdayText is None:
            await ctx.send("Hãy nhập ngày sinh theo dạng `cg sn 01-12-2000`.")
            return

        result = self.memberBirthdayService.setBirthday(ctx.author.id, birthdayText)
        await ctx.send(result["message"])


async def setup(bot):
    await bot.add_cog(MemberBirthday(bot))