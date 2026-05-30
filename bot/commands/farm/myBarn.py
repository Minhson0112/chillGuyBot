import discord
from discord.ext import commands

from bot.services.farm.farmInventoryRenderService import FarmInventoryRenderService
from bot.views.farm.myBarnPaginationView import MyBarnPaginationView


class MyBarnCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.farmInventoryRenderService = FarmInventoryRenderService()

    @commands.command(name="mybarn")
    async def myBarn(self, ctx, page: int = 1):
        try:
            renderResult = self.farmInventoryRenderService.renderBarnPageToBuffer(
                userId=ctx.author.id,
                memberDisplayName=ctx.author.display_name,
                page=page,
            )

            file = discord.File(
                renderResult["buffer"],
                filename="my_barn.png",
            )

            view = MyBarnPaginationView(
                authorId=ctx.author.id,
                memberDisplayName=ctx.author.display_name,
                currentPage=renderResult["currentPage"],
                totalPage=renderResult["totalPage"],
            )

            await ctx.reply(file=file, view=view)

        except FileNotFoundError as e:
            print(f"Barn asset file not found: {e}")
            await ctx.reply("Không tìm thấy ảnh asset để render barn.")

        except Exception as e:
            print(f"Render barn error: {e}")
            await ctx.reply("Đã xảy ra lỗi khi render barn.")


async def setup(bot):
    await bot.add_cog(MyBarnCommand(bot))