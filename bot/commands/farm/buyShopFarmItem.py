from discord.ext import commands

from bot.services.farm.farmBuyShopService import FarmBuyShopService


class BuyShopFarmItemCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.farmBuyShopService = FarmBuyShopService()

    @commands.command(name="buyshop")
    async def buyShop(self, ctx, listingId: int = None):
        if listingId is None:
            await ctx.reply("Cách dùng: `cg buyshop <id món hàng trong shop>`")
            return

        try:
            buyShopResult = self.farmBuyShopService.buyShopItem(
                buyerUserId=ctx.author.id,
                listingId=listingId,
            )

            await ctx.reply(buyShopResult["message"])

        except Exception as e:
            print(f"Buy shop item error: {e}")
            await ctx.reply("Đã xảy ra lỗi khi mua item trong shop.")

async def setup(bot):
    await bot.add_cog(BuyShopFarmItemCommand(bot))