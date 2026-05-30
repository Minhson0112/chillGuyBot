from discord.ext import commands

from bot.services.farm.farmCookService import FarmCookService


class FarmCookCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.farmCookService = FarmCookService()

    @commands.command(name="cook")
    async def cook(self, ctx, resultItemId: int = None, cookingQuantity: int = 1):
        if resultItemId is None:
            await ctx.reply("Cách dùng: `cg cook {id món ăn} {số lượng muốn nấu}`")
            return

        try:
            cookResult = self.farmCookService.cook(
                userId=ctx.author.id,
                resultItemId=resultItemId,
                cookingQuantity=cookingQuantity,
            )

            await ctx.reply(cookResult["message"])

        except Exception as e:
            print(f"Cook food error: {e}")
            await ctx.reply("Đã xảy ra lỗi khi nấu ăn.")


async def setup(bot):
    await bot.add_cog(FarmCookCommand(bot))