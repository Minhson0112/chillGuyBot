from datetime import datetime, timedelta, timezone

import discord

from bot.config.database import getDbSession
from bot.config.emoji import SATURN, SUN
from bot.helper.numberFormatHelper import formatNumber
from bot.helper.timeFormatHelper import formatMillisecondsMinutesSeconds
from bot.repository.mergeGamePlayHistoryRepository import MergeGamePlayHistoryRepository


class MyMergeGameService:
    def __init__(self):
        self.gmt7 = timezone(timedelta(hours=7))

    async def sendMemberStatsMessage(self, ctx):
        memberStats, targetYear, targetMonth = self.findMemberStats(ctx.author.id)
        embed = self.buildMemberStatsEmbed(
            ctx.author,
            memberStats,
            targetYear,
            targetMonth,
        )

        await ctx.reply(embed=embed, mention_author=False)

    def findMemberStats(self, userId: int):
        nowGmt7 = datetime.now(self.gmt7)
        targetYear = nowGmt7.year
        targetMonth = nowGmt7.month

        with getDbSession() as session:
            mergeGamePlayHistoryRepository = MergeGamePlayHistoryRepository(session)
            memberStats = mergeGamePlayHistoryRepository.findMemberStatsByMonth(
                userId,
                targetYear,
                targetMonth,
            )

        return memberStats, targetYear, targetMonth

    def buildMemberStatsEmbed(self, member, memberStats, year: int, month: int):
        bestScore = self.formatOptionalNumber(memberStats.best_score)
        fastestSunTime = formatMillisecondsMinutesSeconds(memberStats.fastest_sun_time)

        embed = discord.Embed(
            title=f"Mergeverse của {member.display_name} - {month:02d}/{year}",
            color=discord.Color.gold(),
        )
        embed.add_field(
            name=f"{SATURN} Điểm cao nhất",
            value=bestScore,
            inline=False,
        )
        embed.add_field(
            name=f"{SUN} Mặt trời nhanh nhất",
            value=fastestSunTime,
            inline=False,
        )
        embed.set_thumbnail(url=member.display_avatar.url)

        if memberStats.best_score is None:
            embed.description = "Chưa có dữ liệu chơi game trong tháng này."

        return embed

    def formatOptionalNumber(self, value):
        if value is None:
            return "--"

        return formatNumber(int(value))
