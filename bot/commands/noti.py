from discord.ext import commands

from bot.services.member.memberNotificationService import MemberNotificationService


class NotiCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.memberNotificationService = MemberNotificationService()

    @commands.command(name="noti")
    async def noti(
        self,
        ctx: commands.Context,
        mode: str = None,
    ):
        if ctx.guild is None:
            return

        result = self.memberNotificationService.updateFarmNotificationSetting(
            userId=ctx.author.id,
            mode=mode,
        )

        await ctx.reply(
            result["message"],
            mention_author=False,
        )


async def setup(bot):
    await bot.add_cog(NotiCommand(bot))
