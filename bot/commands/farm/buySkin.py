from discord.ext import commands

from bot.services.farm.farmBaseSkinBuyService import FarmBaseSkinBuyService


class BuySkinCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.farmBaseSkinBuyService = FarmBaseSkinBuyService()

    @commands.command(name="buyskin")
    async def buySkin(self, ctx, baseSkinId: int = None):
        if baseSkinId is None:
            await ctx.reply("Cách dùng: `cg buyskin <id skin>`")
            return

        try:
            result = self.farmBaseSkinBuyService.buyBaseSkin(
                userId=ctx.author.id,
                baseSkinId=baseSkinId,
            )

            await ctx.reply(result["message"])

        except Exception as e:
            print(f"Buy base skin error: {e}")
            await ctx.reply("Đã xảy ra lỗi khi mua base skin.")


async def setup(bot):
    await bot.add_cog(BuySkinCommand(bot))
