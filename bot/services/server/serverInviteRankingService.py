import discord

from bot.config.database import getDbSession
from bot.config.decoration import FOOTER_DECORATION_IMG_URL
from bot.helper.numberFormatHelper import formatNumber
from bot.repository.serverInviteRepository import ServerInviteRepository


class ServerInviteRankingService:
    def findTopInviters(self, limit: int = 10):
        with getDbSession() as session:
            serverInviteRepository = ServerInviteRepository(session)
            return serverInviteRepository.findTopInviters(limit)

    def buildTopInviteRankingEmbed(self, guild: discord.Guild):
        topInviters = self.findTopInviters(10)

        embed = discord.Embed(
            title="Bảng Xếp Hạng Mời Thành Viên",
            description="Top 10 người mời được nhiều thành viên vào server nhất từ trước đến nay.",
            color=discord.Color.gold(),
        )

        if len(topInviters) == 0:
            embed.add_field(
                name="Chưa có dữ liệu",
                value="Hiện tại chưa có invite nào có lượt sử dụng được ghi nhận.",
                inline=False,
            )
            return embed

        leaderboardText = ""
        totalInvitedCount = 0

        for index, row in enumerate(topInviters, start=1):
            totalUses = int(row.totalUses or 0)
            totalInvitedCount += totalUses

            leaderboardText += (
                f"Top {index}: <@{row.inviterUserId}> - "
                f"Mời được **{formatNumber(totalUses)}** người\n"
            )

        embed.add_field(
            name="BXH Invite",
            value=leaderboardText.strip(),
            inline=False,
        )

        topOne = topInviters[0]
        embed.set_footer(
            text=(
                f"Top 1 hiện tại: {formatNumber(int(topOne.totalUses or 0))} người "
                f"| Tổng top 10: {formatNumber(totalInvitedCount)} người"
            )
        )

        if guild.icon is not None:
            embed.set_thumbnail(url=guild.icon.url)

        embed.set_image(url=FOOTER_DECORATION_IMG_URL)

        return embed
