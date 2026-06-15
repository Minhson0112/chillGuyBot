from discord.ext import commands

from bot.services.donate.donateRankingService import DonateRankingService


class TopDonate(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.donateRankingService = DonateRankingService()

    @commands.command(name="topdn")
    async def topDonate(self, ctx):
        if ctx.guild is None:
            await ctx.send("Lệnh này chỉ dùng được trong server.")
            return

        embed = self.donateRankingService.buildTopDonateEmbed(ctx.guild)
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(TopDonate(bot))
