import discord
from discord.ext import commands

from bot.config.emoji import LOGO
from bot.helper.numberFormatHelper import formatNumber
from bot.services.serverItem.serverItemPurchaseCancelService import ServerItemPurchaseCancelService


class CancelLoveShopCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.serverItemPurchaseCancelService = ServerItemPurchaseCancelService()

    @commands.command(name="cancelloveshop")
    async def cancelLoveShop(self, ctx: commands.Context):
        if ctx.guild is None:
            return

        result = self.serverItemPurchaseCancelService.cancelPendingPurchases(
            userId=ctx.author.id,
        )

        if not result["success"]:
            await ctx.reply(
                f"{LOGO} {result['message']}",
                mention_author=False,
            )
            return

        itemText = self.buildCancelledItemText(result["cancelledItems"])

        await ctx.reply(
            content=ctx.author.mention,
            embed=self.buildCancelLoveShopEmbed(
                message=result["message"],
                itemText=itemText,
            ),
            allowed_mentions=discord.AllowedMentions(
                users=True,
                roles=False,
                everyone=False,
            ),
            mention_author=False,
        )

    def buildCancelledItemText(self, cancelledItems):
        return ", ".join([
            f"{self.buildItemText(item)} x**{formatNumber(item['quantity'])}**"
            for item in cancelledItems
        ])

    def buildItemText(self, item):
        if item["emoji"] is None:
            return f"**{item['name']}**"

        return f"{item['emoji']} **{item['name']}**"

    def buildCancelLoveShopEmbed(
        self,
        message: str,
        itemText: str,
    ):
        embed = discord.Embed(
            title="Đã hủy giao dịch love shop",
            description=(
                f"{message}\n\n"
                f"Item đã hủy: {itemText}"
            ),
            color=discord.Color.orange(),
        )

        return embed


async def setup(bot):
    await bot.add_cog(CancelLoveShopCommand(bot))
