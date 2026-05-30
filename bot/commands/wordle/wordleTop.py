from discord.ext import commands

from bot.services.wordle.wordleRankingService import WordleRankingService


class WordleTop(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.wordleRankingService = WordleRankingService()

    @commands.command(name="topw")
    async def topWordle(self, ctx):
        if ctx.guild is None:
            await ctx.send("Lệnh này chỉ dùng được trong server.")
            return

        embed = self.wordleRankingService.buildTopRankingEmbed(ctx.guild)
        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(WordleTop(bot))
