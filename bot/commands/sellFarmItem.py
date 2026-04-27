from discord.ext import commands

from bot.services.farm.farmItemSellService import FarmItemSellService


class SellFarmItemCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.farmItemSellService = FarmItemSellService()

    @commands.command(name="sell")
    async def sell(self, ctx, inventoryId: int = None, quantity: int = 1):
        if inventoryId is None:
            await ctx.reply("Cách dùng: `cg sell <id item trong kho> <số lượng>`")
            return

        try:
            sellResult = self.farmItemSellService.sellItem(
                userId=ctx.author.id,
                inventoryId=inventoryId,
                quantity=quantity,
            )

            await ctx.reply(sellResult["message"])

        except Exception as e:
            print(f"Sell farm item error: {e}")
            await ctx.reply("Đã xảy ra lỗi khi bán item.")


async def setup(bot):
    await bot.add_cog(SellFarmItemCommand(bot))