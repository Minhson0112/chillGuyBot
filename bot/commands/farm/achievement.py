from discord.ext import commands

from bot.services.farm.farmAchievementService import FarmAchievementService
from bot.views.farm.farmAchievementPaginationView import (
    FarmAchievementPaginationView,
    buildFarmAchievementEmbed,
)


class FarmAchievementCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.farmAchievementService = FarmAchievementService()

    @commands.command(name="ach")
    async def achievement(self, ctx):
        try:
            pageResult = self.farmAchievementService.getAchievementPage(
                userId=ctx.author.id,
                page=1,
            )

            if not pageResult["success"]:
                await ctx.reply(pageResult["message"])
                return

            view = FarmAchievementPaginationView(
                authorId=ctx.author.id,
                currentPage=pageResult["currentPage"],
                totalPage=pageResult["totalPage"],
            )
            embed = buildFarmAchievementEmbed(pageResult)

            await ctx.reply(embed=embed, view=view)
        except Exception as e:
            print(f"Farm achievement command error: {e}")
            await ctx.reply("Đã xảy ra lỗi khi mở bảng thành tựu farm.")


async def setup(bot):
    await bot.add_cog(FarmAchievementCommand(bot))
