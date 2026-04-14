import discord
from discord.ext import commands

from bot.config.emoji import LOGO
from bot.config.database import getDbSession
from bot.repository.owoDonateHistoryRepository import OwoDonateHistoryRepository


class TopDonate(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="topdn")
    async def topDonate(self, ctx):
        if ctx.guild is None:
            await ctx.send("Lệnh này chỉ dùng được trong server.")
            return

        with getDbSession() as session:
            owoDonateHistoryRepository = OwoDonateHistoryRepository(session)
            topDonators = owoDonateHistoryRepository.getTopDonators(limit=10)

        if not topDonators:
            await ctx.send("Hiện tại chưa có dữ liệu donate.")
            return

        embed = discord.Embed(
            title="Top 10 Donate Leaderboard",
            description=f"{LOGO}\nCảm ơn tất cả những tấm lòng đã ủng hộ server.",
        )

        medals = {
            1: "🥇",
            2: "🥈",
            3: "🥉",
        }

        leaderboardText = ""

        for index, row in enumerate(topDonators, start=1):
            member = ctx.guild.get_member(row.sender_user_id)
            memberText = member.mention if member is not None else f"<@{row.sender_user_id}>"
            rankText = medals.get(index, f"`#{index}`")

            leaderboardText += (
                f"{rankText} {memberText}\n"
                f"┗ **{row.totalDonate:,}** cowoncy\n\n"
            )

        embed.add_field(
            name="BXH Donate",
            value=leaderboardText.strip(),
            inline=False,
        )

        topOne = topDonators[0]
        embed.set_footer(
            text=f"Top 1 hiện tại: {topOne.totalDonate:,} cowoncy"
        )

        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(TopDonate(bot))