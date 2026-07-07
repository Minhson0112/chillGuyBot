import discord
from discord.ext import commands

from bot.services.serverItem.coupleBreakupService import CoupleBreakupService


class BreakupCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.coupleBreakupService = CoupleBreakupService()

    @commands.command(name="breakup")
    async def breakup(self, ctx: commands.Context):
        if ctx.guild is None:
            return

        result = self.coupleBreakupService.breakupCurrentCouple(ctx.author.id)

        if not result["success"]:
            await ctx.reply(
                result["message"],
                mention_author=False,
            )
            return

        await ctx.reply(
            embed=self.buildBreakupEmbed(ctx.author, result["partnerUserId"]),
            allowed_mentions=discord.AllowedMentions(
                users=True,
                roles=False,
                everyone=False,
            ),
            mention_author=False,
        )

    def buildBreakupEmbed(self, author: discord.Member, partnerUserId: int):
        return discord.Embed(
            title="Đã chấm dứt mối quan hệ",
            description=(
                f"{author.mention} đã chấm dứt mối quan hệ hiện tại với "
                f"<@{partnerUserId}>."
            ),
            color=discord.Color.red(),
        )


async def setup(bot):
    await bot.add_cog(BreakupCommand(bot))
