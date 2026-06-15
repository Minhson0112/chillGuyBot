from datetime import datetime, timedelta, timezone

import discord

from bot.config.database import getDbSession
from bot.config.emoji import COWONCCY, LOGO
from bot.repository.owoDonateHistoryRepository import OwoDonateHistoryRepository


class DonateRankingService:
    GMT7 = timezone(timedelta(hours=7))

    def findTopDonators(self, limit: int = 10):
        with getDbSession() as session:
            owoDonateHistoryRepository = OwoDonateHistoryRepository(session)
            return owoDonateHistoryRepository.getTopDonators(limit=limit)

    def findTopMonthlyDonators(self, year: int, month: int, limit: int = 10):
        with getDbSession() as session:
            owoDonateHistoryRepository = OwoDonateHistoryRepository(session)
            return owoDonateHistoryRepository.getTopDonatorsByMonth(
                year=year,
                month=month,
                limit=limit,
            )

    def buildTopDonateEmbed(self, guild: discord.Guild) -> discord.Embed:
        topDonators = self.findTopDonators(limit=10)

        return self.buildDonateRankingEmbed(
            guild=guild,
            topDonators=topDonators,
            title="Top 10 Donate Leaderboard",
            emptyMessage="Hiện tại chưa có dữ liệu donate.",
        )

    def buildTopMonthlyDonateEmbed(self, guild: discord.Guild) -> discord.Embed:
        nowGmt7 = datetime.now(self.GMT7)
        targetYear = nowGmt7.year
        targetMonth = nowGmt7.month
        topDonators = self.findTopMonthlyDonators(
            year=targetYear,
            month=targetMonth,
            limit=10,
        )

        return self.buildDonateRankingEmbed(
            guild=guild,
            topDonators=topDonators,
            title=f"Top 10 Donate Leaderboard - {targetMonth:02d}/{targetYear}",
            emptyMessage="Hiện tại chưa có dữ liệu donate trong tháng này.",
        )

    def buildDonateRankingEmbed(
        self,
        guild: discord.Guild,
        topDonators,
        title: str,
        emptyMessage: str,
    ) -> discord.Embed:
        embed = discord.Embed(
            title=title,
            description=f"{LOGO}\nCảm ơn tất cả những tấm lòng đã ủng hộ server.",
        )

        if not topDonators:
            embed.add_field(
                name="Chưa có dữ liệu",
                value=emptyMessage,
                inline=False,
            )
            return embed

        medals = {
            1: "🥇",
            2: "🥈",
            3: "🥉",
        }

        leaderboardText = ""

        for index, row in enumerate(topDonators, start=1):
            member = guild.get_member(row.sender_user_id)
            memberText = member.mention if member is not None else f"<@{row.sender_user_id}>"
            rankText = medals.get(index, f"`#{index}`")

            leaderboardText += (
                f"{rankText} {memberText}\n"
                f"┗ **{row.totalDonate:,}** cowoncy {COWONCCY}\n\n"
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

        return embed
