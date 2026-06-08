import discord
from discord.ext import commands

from bot.config.emoji import LOGO
from bot.services.lotto.lottoTicketPurchaseCancelService import LottoTicketPurchaseCancelService


class CancelLottoCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.lottoTicketPurchaseCancelService = LottoTicketPurchaseCancelService()

    @commands.command(name="cancellotto")
    async def cancelLotto(self, ctx: commands.Context):
        if ctx.guild is None:
            return

        result = self.lottoTicketPurchaseCancelService.cancelPendingPurchases(
            userId=ctx.author.id,
        )

        if not result["success"]:
            await ctx.reply(
                f"{LOGO} {result['message']}",
                mention_author=False,
            )
            return

        await ctx.reply(
            content=ctx.author.mention,
            embed=self.buildCancelLottoEmbed(
                message=result["message"],
                cancelledPurchases=result["cancelledPurchases"],
            ),
            allowed_mentions=discord.AllowedMentions(
                users=True,
                roles=False,
                everyone=False,
            ),
            mention_author=False,
        )

    def buildCancelLottoEmbed(
        self,
        message: str,
        cancelledPurchases: list[dict],
    ):
        embed = discord.Embed(
            title="Đã hủy giao dịch mua vé lotto",
            description=message,
            color=discord.Color.orange(),
        )

        for cancelledPurchase in cancelledPurchases:
            lottoEventName = cancelledPurchase["lottoEventName"]

            if lottoEventName is None:
                lottoEventName = f"#{cancelledPurchase['lottoEventId']}"

            embed.add_field(
                name=lottoEventName,
                value=f"Số vé đã hủy: **{cancelledPurchase['ticketQuantity']}**",
                inline=False,
            )

        return embed


async def setup(bot):
    await bot.add_cog(CancelLottoCommand(bot))
