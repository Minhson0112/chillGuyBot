from datetime import datetime, timedelta, timezone

from discord.ext import commands

from bot.config.database import getDbSession
from bot.repository.memberDailyActivityRepository import MemberDailyActivityRepository


class MyVoiceRank(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.gmt7 = timezone(timedelta(hours=7))

    @commands.command(name="myv")
    async def myVoiceRank(self, ctx):
        if ctx.guild is None:
            await ctx.reply(
                "Lệnh này chỉ có thể dùng trong server.",
                mention_author=False,
            )
            return

        nowGmt7 = datetime.now(self.gmt7)
        targetYear = nowGmt7.year
        targetMonth = nowGmt7.month

        with getDbSession() as session:
            memberDailyActivityRepository = MemberDailyActivityRepository(session)
            rankData = memberDailyActivityRepository.findVoiceRankByMonth(
                ctx.author.id,
                targetYear,
                targetMonth,
            )

        if rankData is None:
            await ctx.reply(
                f"{ctx.author.mention} tháng **{targetMonth}/{targetYear}** bạn chưa có thời gian voice nào trong bảng xếp hạng.",
                mention_author=False,
            )
            return

        voiceTime = self.formatVoiceSeconds(rankData["voice_seconds"])
        rank = rankData["rank"]
        totalRankedMemberCount = rankData["total_ranked_member_count"]

        await ctx.reply(
            f"{ctx.author.mention} hiện đang xếp hạng **#{rank}** trên **{totalRankedMemberCount}** người trong bảng xếp hạng voice tháng **{targetMonth}/{targetYear}**.\n"
            f"Thời gian voice: **{voiceTime}**",
            mention_author=False,
        )

    def formatVoiceSeconds(self, value):
        totalSeconds = int(value)

        hours = totalSeconds // 3600
        minutes = (totalSeconds % 3600) // 60
        seconds = totalSeconds % 60

        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


async def setup(bot):
    await bot.add_cog(MyVoiceRank(bot))