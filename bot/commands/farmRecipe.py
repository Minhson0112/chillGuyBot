import discord
from discord.ext import commands

from bot.services.farm.farmRecipeRenderService import FarmRecipeRenderService
from bot.views.farm.farmRecipePaginationView import FarmRecipePaginationView


class FarmRecipeCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.farmRecipeRenderService = FarmRecipeRenderService()

    @commands.command(name="rec")
    async def recipes(self, ctx):
        try:
            renderResult = self.farmRecipeRenderService.renderRecipePageToBuffer(page=1)

            file = discord.File(
                renderResult["buffer"],
                filename="recipes.png",
            )

            view = FarmRecipePaginationView(
                authorId=ctx.author.id,
                currentPage=renderResult["currentPage"],
                totalPage=renderResult["totalPage"],
            )

            await ctx.reply(
                content=FarmRecipePaginationView.COOK_GUIDE_TEXT,
                file=file,
                view=view,
            )

        except FileNotFoundError as e:
            print(f"Recipe asset file not found: {e}")
            await ctx.reply("Không tìm thấy ảnh asset để render công thức nấu ăn.")

        except Exception as e:
            print(f"Render recipe error: {e}")
            await ctx.reply("Đã xảy ra lỗi khi render công thức nấu ăn.")


async def setup(bot):
    await bot.add_cog(FarmRecipeCommand(bot))