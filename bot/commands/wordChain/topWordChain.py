from discord.ext import commands

from bot.services.wordChain.wordChainRankingComponentService import WordChainRankingComponentService


class TopWordChain(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.wordChainRankingComponentService = WordChainRankingComponentService(bot)

    @commands.command(name="topn")
    async def topWordChain(self, ctx, month: int | None = None):
        if ctx.guild is None:
            await ctx.reply("Lệnh này chỉ dùng được trong server.", mention_author=False)
            return

        if month is not None and (month < 1 or month > 12):
            await ctx.reply("Tháng không hợp lệ. Hãy nhập từ 1 đến 12.", mention_author=False)
            return

        await self.wordChainRankingComponentService.sendTopMembersMessage(ctx, month)


async def setup(bot):
    await bot.add_cog(TopWordChain(bot))
