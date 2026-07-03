import discord
from discord.ext import commands

from bot.config.emoji import FARM_GAME_EMOJI, WARNING
from bot.helper.numberFormatHelper import formatNumber
from bot.services.farm.farmItemSellService import FarmItemSellService
from bot.views.farm.sellFarmItemView import SellFarmItemView


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
            sellPreview = self.farmItemSellService.getSellPreview(
                userId=ctx.author.id,
                inventoryId=inventoryId,
                quantity=quantity,
            )

            if not sellPreview["success"]:
                await ctx.reply(sellPreview["message"])
                return

            chillCoinEmoji = FARM_GAME_EMOJI["chill_coin"]
            embed = discord.Embed(
                title="Xác nhận bán item",
                description=(
                    f"Bạn có chắc chắn muốn bán **{quantity}** {sellPreview['itemText']} "
                    f"với **{formatNumber(sellPreview['totalPrice'])}** {chillCoinEmoji} không?\n\n"
                    f"{WARNING} Bán bằng lệnh này sẽ chỉ nhận **80%** giá trị gốc của item."
                ),
                color=discord.Color.gold(),
            )
            embed.set_footer(text="Bấm xác nhận để bán item hoặc hủy để dừng lại.")

            view = SellFarmItemView(
                authorId=ctx.author.id,
                inventoryId=inventoryId,
                quantity=quantity,
            )
            message = await ctx.reply(
                embed=embed,
                view=view,
                allowed_mentions=discord.AllowedMentions.none(),
            )
            view.message = message

        except Exception as e:
            print(f"Sell farm item error: {e}")
            await ctx.reply("Đã xảy ra lỗi khi bán item.")


async def setup(bot):
    await bot.add_cog(SellFarmItemCommand(bot))
