from discord.ext import commands

from bot.services.farm.farmBuyShopService import FarmBuyShopService
from bot.services.farm.farmMarketNotificationService import FarmMarketNotificationService


class BuyShopFarmItemCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.farmBuyShopService = FarmBuyShopService()
        self.farmMarketNotificationService = FarmMarketNotificationService()

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

            if buyShopResult["success"]:
                try:
                    await self.farmMarketNotificationService.sendMemberPurchaseNotification(
                        bot=self.bot,
                        notificationData=buyShopResult.get("notificationData"),
                    )
                except Exception as e:
                    print(f"Farm market purchase notification error: {e}")

        except Exception as e:
            print(f"Buy shop item error: {e}")
            await ctx.reply("Đã xảy ra lỗi khi mua item trong shop.")

async def setup(bot):
    await bot.add_cog(BuyShopFarmItemCommand(bot))
