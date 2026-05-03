from discord.ext import commands

from bot.services.farm.dailyCheckinService import DailyCheckinService


class Daily(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.dailyCheckinService = DailyCheckinService()

    @commands.command(name="daily")
    async def daily(self, ctx):
        try:
            result = self.dailyCheckinService.checkin(ctx.author.id)

            await ctx.reply(result["message"])

        except Exception as e:
            print(f"Daily checkin error: {e}")
            await ctx.reply("Đã xảy ra lỗi khi điểm danh.")


async def setup(bot):
    await bot.add_cog(Daily(bot))