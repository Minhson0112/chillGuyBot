import discord
from discord.ext import commands

from bot.services.farm.farmInventoryRenderService import FarmInventoryRenderService
from bot.views.farm.mySiloPaginationView import MySiloPaginationView


class MySiloCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.farmInventoryRenderService = FarmInventoryRenderService()

    @commands.command(name="mysilo")
    async def mySilo(self, ctx, page: int = 1):
        try:
            renderResult = self.farmInventoryRenderService.renderSiloPageToBuffer(
                userId=ctx.author.id,
                memberDisplayName=ctx.author.display_name,
                page=page,
            )

            file = discord.File(
                renderResult["buffer"],
                filename="my_silo.png",
            )

            view = MySiloPaginationView(
                authorId=ctx.author.id,
                memberDisplayName=ctx.author.display_name,
                currentPage=renderResult["currentPage"],
                totalPage=renderResult["totalPage"],
            )

            await ctx.reply(file=file, view=view)

        except FileNotFoundError as e:
            print(f"Silo asset file not found: {e}")
            await ctx.reply("Không tìm thấy ảnh asset để render silo.")

        except Exception as e:
            print(f"Render silo error: {e}")
            await ctx.reply("Đã xảy ra lỗi khi render silo.")


async def setup(bot):
    await bot.add_cog(MySiloCommand(bot))