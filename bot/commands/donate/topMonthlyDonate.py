from discord.ext import commands

from bot.services.donate.donateRankingService import DonateRankingService


class TopMonthlyDonate(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.donateRankingService = DonateRankingService()

    @commands.command(name="topmdn")
    async def topMonthlyDonate(self, ctx):
        if ctx.guild is None:
            await ctx.send("Lệnh này chỉ dùng được trong server.")
            return

        embed = self.donateRankingService.buildTopMonthlyDonateEmbed(ctx.guild)
        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(TopMonthlyDonate(bot))
