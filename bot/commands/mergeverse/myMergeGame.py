from discord.ext import commands

from bot.services.mergeGame.myMergeGameService import MyMergeGameService


class MyMergeGame(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.myMergeGameService = MyMergeGameService()

    @commands.command(name="mymerge")
    async def myMergeGame(self, ctx):
        if ctx.guild is None:
            await ctx.reply("lệnh này chỉ có thể sử dụng trong server.", mention_author=False)
            return

        await self.myMergeGameService.sendMemberStatsMessage(ctx)


async def setup(bot):
    await bot.add_cog(MyMergeGame(bot))
