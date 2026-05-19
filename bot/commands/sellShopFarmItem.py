from discord.ext import commands

from bot.services.farm.farmSellShopService import FarmSellShopService


class SellShopFarmItemCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.farmSellShopService = FarmSellShopService()

    @commands.command(name="sellshop")
    async def sellShop(self, ctx, inventoryId: int = None, quantity: int = 1):
        if inventoryId is None:
            await ctx.reply("Cách dùng: `cg sellshop <id item trong kho> <số lượng>`")
            return

        try:
            sellShopResult = self.farmSellShopService.sellShopItem(
                userId=ctx.author.id,
                inventoryId=inventoryId,
                quantity=quantity,
            )

            await ctx.reply(sellShopResult["message"])

        except Exception as e:
            print(f"Sell shop farm item error: {e}")
            await ctx.reply("Đã xảy ra lỗi khi đăng bán item lên shop riêng.")


async def setup(bot):
    await bot.add_cog(SellShopFarmItemCommand(bot))