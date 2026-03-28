import discord

from bot.config.database import getDbSession
from bot.repository.memberRepository import MemberRepository


class WordleRankingService:
    def buildTopRankingEmbed(self, guild: discord.Guild) -> discord.Embed:
        with getDbSession() as session:
            memberRepository = MemberRepository(session)
            topMembers = memberRepository.findTopCorrectWordGuessMembers(10)

        embed = discord.Embed(
            title="Wordle Ranking",
            description="Top 10 người chơi đoán đúng nhiều từ nhất",
        )

        if guild.icon is not None:
            embed.set_thumbnail(url=guild.icon.url)

        if not topMembers:
            embed.add_field(
                name="Chưa có dữ liệu",
                value="Hiện tại chưa có ai đoán đúng từ nào.",
                inline=False,
            )
            return embed

        rankingLines = []
        medalMap = {
            1: "🥇",
            2: "🥈",
            3: "🥉",
        }

        for index, member in enumerate(topMembers, start=1):
            displayName = member.global_name or member.username
            prefix = medalMap.get(index, f"`#{index}`")
            rankingLines.append(
                f"{prefix} **{displayName}** — **{member.correct_word_guess_count}** lần"
            )

        embed.add_field(
            name="Bảng xếp hạng",
            value="\n".join(rankingLines),
            inline=False,
        )

        embed.set_footer(text=f"Tổng số người trong top: {len(topMembers)}")
        return embed