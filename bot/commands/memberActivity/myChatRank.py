from datetime import datetime, timedelta, timezone

from discord.ext import commands

from bot.config.database import getDbSession
from bot.helper.numberFormatHelper import formatNumber
from bot.repository.memberDailyActivityRepository import MemberDailyActivityRepository


class MyChatRank(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.gmt7 = timezone(timedelta(hours=7))

    @commands.command(name="myc")
    async def myChatRank(self, ctx):
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
            rankData = memberDailyActivityRepository.findLevelChatRankByMonth(
                ctx.author.id,
                targetYear,
                targetMonth,
            )

        if rankData is None:
            await ctx.reply(
                f"{ctx.author.mention} tháng **{targetMonth}/{targetYear}** bạn chưa có tin nhắn hợp lệ nào trong bảng xếp hạng chat.",
                mention_author=False,
            )
            return

        chatCount = formatNumber(int(rankData["level_chat_count"]))
        rank = rankData["rank"]
        totalRankedMemberCount = rankData["total_ranked_member_count"]

        await ctx.reply(
            f"{ctx.author.mention} hiện đang xếp hạng **#{rank}** trên **{totalRankedMemberCount}** người trong bảng xếp hạng chat tháng **{targetMonth}/{targetYear}**.\n"
            f"Số tin nhắn hợp lệ: **{chatCount}**",
            mention_author=False,
        )


async def setup(bot):
    await bot.add_cog(MyChatRank(bot))
