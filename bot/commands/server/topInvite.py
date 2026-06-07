from discord.ext import commands

from bot.services.server.serverInviteRankingService import ServerInviteRankingService


class TopInviteCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.serverInviteRankingService = ServerInviteRankingService()

    @commands.command(name="topinv")
    async def topInvite(self, ctx):
        if ctx.guild is None:
            await ctx.send("Lệnh này chỉ dùng được trong server.")
            return

        embed = self.serverInviteRankingService.buildTopInviteRankingEmbed(ctx.guild)

        await ctx.reply(
            embed=embed,
            mention_author=False,
        )


async def setup(bot):
    await bot.add_cog(TopInviteCommand(bot))
