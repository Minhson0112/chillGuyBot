from discord.ext import commands

from bot.services.farm.dailyTaskService import DailyTaskService


class Task(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.dailyTaskService = DailyTaskService()

    @commands.command(name="task")
    async def task(self, ctx):
        try:
            result = self.dailyTaskService.getOrCreateTodayTasks(ctx.author.id)

            await ctx.reply(result["message"])

        except Exception as e:
            print(f"Daily task error: {e}")
            await ctx.reply("Đã xảy ra lỗi khi hiển thị daily task.")


async def setup(bot):
    await bot.add_cog(Task(bot))