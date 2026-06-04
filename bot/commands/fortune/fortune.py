import asyncio

import discord
from discord.ext import commands

from bot.services.fortune.dailyFortuneService import DailyFortuneService


class Fortune(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.dailyFortuneService = DailyFortuneService()

    @commands.command(name="fortune")
    async def fortune(self, ctx):
        try:
            result = await asyncio.to_thread(
                self.dailyFortuneService.getDailyFortune,
                ctx.author.id,
            )

            if result["success"] is False:
                await ctx.reply(result["message"], mention_author=False)
                return

            dailyFortune = result["dailyFortune"]

            if dailyFortune is None:
                await ctx.reply("Không tìm thấy Daily Fortune hôm nay.", mention_author=False)
                return

            await ctx.reply(
                embed=self.buildDailyFortuneEmbed(ctx.author, dailyFortune),
                mention_author=False,
            )
        except Exception as e:
            print(f"Daily fortune command error: {e}")
            await ctx.reply("Đã xảy ra lỗi khi xem Daily Fortune.", mention_author=False)

    def buildDailyFortuneEmbed(self, member, dailyFortune):
        embed = discord.Embed(
            title="🔮 Daily Fortune",
            description=(
                f"- <a:CS_hoaaa:1510626671735079073> May Mắn: {dailyFortune.luck_rate}/100\n"
                f"- <a:CS_pinkx5:1507030282451292335> Tình Cảm: {dailyFortune.love_rate}/100\n"
                f"- <a:CS_purple1:1507030284976128050> Công Việc | Học Tập: {dailyFortune.career_rate}/100\n\n"
                f"{dailyFortune.description}"
            ),
            color=discord.Color.purple(),
        )
        embed.set_thumbnail(url=member.display_avatar.url)

        return embed


async def setup(bot):
    await bot.add_cog(Fortune(bot))
