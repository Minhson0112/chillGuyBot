from discord.ext import commands

from bot.services.serverItem.serverItemShopMessageService import ServerItemShopMessageService


class LoveShopCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.serverItemShopMessageService = ServerItemShopMessageService()

    @commands.command(name="loveshop")
    async def loveShop(self, ctx):
        try:
            await self.serverItemShopMessageService.sendShopMessage(ctx)
        except Exception as e:
            print(f"Show love shop error: {e}")
            await ctx.reply("Đã xảy ra lỗi khi mở love shop.")


async def setup(bot):
    await bot.add_cog(LoveShopCommand(bot))
