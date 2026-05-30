from discord.ext import commands

from bot.services.farm.farmShopBuyService import FarmShopBuyService


class BuyCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.farmShopBuyService = FarmShopBuyService()

    @commands.command(name="buy")
    async def buy(self, ctx, shopItemId: int = None, quantity: int = 1):
        if shopItemId is None:
            await ctx.reply("Cách dùng: `cg buy <shop_item_id> [số_lượng]`")
            return

        result = self.farmShopBuyService.buyShopItem(
            userId=ctx.author.id,
            shopItemId=shopItemId,
            quantity=quantity,
        )

        await ctx.reply(result["message"])


async def setup(bot):
    await bot.add_cog(BuyCommand(bot))