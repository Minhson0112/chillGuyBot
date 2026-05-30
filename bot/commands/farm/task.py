import discord
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

            if not result["success"]:
                await ctx.reply(result["message"])
                return

            embed = self.buildDailyTaskEmbed(
                ctx=ctx,
                embedData=result["embedData"],
            )

            await ctx.reply(embed=embed)

        except Exception as e:
            print(f"Daily task error: {e}")
            await ctx.reply("Đã xảy ra lỗi khi hiển thị daily task.")

    def buildDailyTaskEmbed(
        self,
        ctx,
        embedData,
    ):
        embed = discord.Embed(
            title=embedData["title"],
            description=embedData["description"],
            color=discord.Color.gold(),
        )

        embed.set_author(
            name=f"Daily task của {ctx.author.display_name}",
            icon_url=ctx.author.display_avatar.url,
        )

        embed.set_thumbnail(url=ctx.author.display_avatar.url)

        for field in embedData["fields"]:
            embed.add_field(
                name=field["name"],
                value=field["value"],
                inline=False,
            )

        embed.set_footer(text=embedData["footer"])

        return embed


async def setup(bot):
    await bot.add_cog(Task(bot))