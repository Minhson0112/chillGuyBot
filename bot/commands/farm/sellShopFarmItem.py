import discord
from discord.ext import commands

from bot.config.emoji import FARM_GAME_EMOJI, GIFT, WARNING
from bot.helper.numberFormatHelper import formatNumber
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

            if not sellShopResult["success"]:
                await ctx.reply(sellShopResult["message"])
                return

            result = sellShopResult["result"]
            chillCoinEmoji = FARM_GAME_EMOJI["chill_coin"]
            embed = discord.Embed(
                title="Đăng bán item thành công",
                description=(
                    f"Bạn đã đăng bán **{result['quantity']}** {result['itemText']} "
                    f"lên shop của bạn với giá "
                    f"**{formatNumber(result['totalMarketPrice'])}** {chillCoinEmoji}.\n"
                    f"ID shop: `{result['listingId']}`\n\n"
                    f"{WARNING} Nếu quá **5 tiếng** mà không có ai mua, Chill Guy sẽ mua "
                    f"với 100% giá gốc là "
                    f"**{formatNumber(result['totalMarketPrice'])}** {chillCoinEmoji}.\n\n"
                    f"{GIFT} Nếu member mua, bạn sẽ nhận được bonus **20%** giá trị item, "
                    f"tổng cộng **{formatNumber(result['memberSellerPayout'])}** "
                    f"{chillCoinEmoji}. Tổng bonus market tối đa mỗi ngày là "
                    f"**{formatNumber(result['dailyMemberSellerBonusLimit'])}** "
                    f"{chillCoinEmoji}."
                ),
                color=discord.Color.green(),
            )

            if result["dailyTaskMessage"] is not None:
                embed.add_field(
                    name="Nhiệm vụ hằng ngày",
                    value=result["dailyTaskMessage"],
                    inline=False,
                )

            await ctx.reply(
                embed=embed,
                allowed_mentions=discord.AllowedMentions.none(),
            )

        except Exception as e:
            print(f"Sell shop farm item error: {e}")
            await ctx.reply("Đã xảy ra lỗi khi đăng bán item lên shop riêng.")


async def setup(bot):
    await bot.add_cog(SellShopFarmItemCommand(bot))
