import discord

from bot.config.database import getDbSession
from bot.config.emoji import LOGO
from bot.repository.owoDonateHistoryRepository import OwoDonateHistoryRepository


class DonateRankingService:
    def findTopDonators(self, limit: int = 10):
        with getDbSession() as session:
            owoDonateHistoryRepository = OwoDonateHistoryRepository(session)
            return owoDonateHistoryRepository.getTopDonators(limit=limit)

    def buildTopDonateEmbed(self, guild: discord.Guild) -> discord.Embed:
        topDonators = self.findTopDonators(limit=10)

        embed = discord.Embed(
            title="Top 10 Donate Leaderboard",
            description=f"{LOGO}\nCảm ơn tất cả những tấm lòng đã ủng hộ server.",
        )

        if not topDonators:
            embed.add_field(
                name="Chưa có dữ liệu",
                value="Hiện tại chưa có dữ liệu donate.",
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

        return embed
