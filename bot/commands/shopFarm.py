import discord
from discord.ext import commands

from bot.services.farm.farmShopRenderService import FarmShopRenderService
from bot.views.farm.farmNpcShopPaginationView import FarmNpcShopPaginationView


class ShopFarmCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.farmShopRenderService = FarmShopRenderService()

    @commands.command(name="shopfarm")
    async def shopFarm(self, ctx, page: int = 1):
        try:
            renderResult = self.farmShopRenderService.renderShopPageToBuffer(page)

            file = discord.File(
                renderResult["buffer"],
                filename="farm_shop.png",
            )

            view = FarmNpcShopPaginationView(
                authorId=ctx.author.id,
                currentPage=renderResult["currentPage"],
                totalPage=renderResult["totalPage"],
            )

            await ctx.reply(file=file, view=view)

        except FileNotFoundError as e:
            print(f"Farm shop asset file not found: {e}")
            await ctx.reply("Không tìm thấy ảnh asset để render shop.")

        except Exception as e:
            print(f"Render farm shop error: {e}")
            await ctx.reply("Đã xảy ra lỗi khi render shop.")


async def setup(bot):
    await bot.add_cog(ShopFarmCommand(bot))