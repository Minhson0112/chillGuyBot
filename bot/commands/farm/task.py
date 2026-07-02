import discord
from discord.ext import commands

from bot.services.farm.dailyTaskImageService import DailyTaskImageService
from bot.services.farm.dailyTaskService import DailyTaskService


class Task(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.dailyTaskService = DailyTaskService()
        self.dailyTaskImageService = DailyTaskImageService()

    @commands.command(name="task")
    async def task(self, ctx):
        try:
            result = self.dailyTaskService.getOrCreateTodayTasks(ctx.author.id)

            if not result["success"]:
                await ctx.reply(result["message"])
                return

            async with ctx.typing():
                imageBuffer = self.dailyTaskImageService.buildDailyTaskImage(
                    result["imageData"],
                )

            file = discord.File(
                fp=imageBuffer,
                filename="daily_task.png",
            )
            await ctx.reply(file=file)

        except Exception as e:
            print(f"Daily task error: {e}")
            await ctx.reply("Đã xảy ra lỗi khi hiển thị daily task.")

async def setup(bot):
    await bot.add_cog(Task(bot))
