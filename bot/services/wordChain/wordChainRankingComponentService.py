from datetime import datetime, timedelta, timezone

from discord.http import Route

from bot.config.database import getDbSession
from bot.config.emoji import PERFECT
from bot.enums.discordComponentType import DiscordComponentType
from bot.helper.numberFormatHelper import formatNumber
from bot.repository.wordChainWinHistoryRepository import WordChainWinHistoryRepository


class WordChainRankingComponentService:
    COMPONENTS_V2_FLAG = 1 << 15

    def __init__(self, bot):
        self.bot = bot
        self.gmt7 = timezone(timedelta(hours=7))

    async def sendTopMembersMessage(self, ctx, month: int | None = None):
        nowGmt7 = datetime.now(self.gmt7)
        targetYear = nowGmt7.year
        targetMonth = month if month is not None else nowGmt7.month
        topMembers = self.findTopMembers(targetYear, targetMonth)
        payload = {
            "flags": self.COMPONENTS_V2_FLAG,
            "allowed_mentions": {
                "parse": [],
            },
            "components": [
                {
                    "type": DiscordComponentType.CONTAINER,
                    "components": self.buildContainerComponents(
                        ctx.guild,
                        topMembers,
                        targetYear,
                        targetMonth,
                    ),
                },
            ],
        }

        await ctx.bot.http.request(
            Route(
                "POST",
                "/channels/{channel_id}/messages",
                channel_id=ctx.channel.id,
            ),
            json=payload,
        )

    def findTopMembers(self, year: int, month: int):
        with getDbSession() as session:
            winHistoryRepository = WordChainWinHistoryRepository(session)
            return winHistoryRepository.findTopWinMembersByMonth(
                year,
                month,
                5,
            )

    def buildContainerComponents(
        self,
        guild,
        topMembers,
        year: int,
        month: int,
    ):
        components = [
            {
                "type": DiscordComponentType.TEXT_DISPLAY,
                "content": f"## Nối chữ Top 5 - {month:02d}/{year}",
            },
            {
                "type": DiscordComponentType.SEPARATOR,
            },
        ]

        if not topMembers:
            components.append({
                "type": DiscordComponentType.TEXT_DISPLAY,
                "content": "Chưa có dữ liệu thắng nối chữ trong tháng này.",
            })
            return self.appendFooterComponents(components)

        for rank, topMember in enumerate(topMembers, start=1):
            components.append(
                self.buildRankingSection(
                    guild,
                    topMember,
                    rank,
                ),
            )

        return self.appendFooterComponents(components)

    def appendFooterComponents(self, components):
        components.extend([
            {
                "type": DiscordComponentType.SEPARATOR,
            },
            {
                "type": DiscordComponentType.TEXT_DISPLAY,
                "content": "-# Top số lần thắng nối chữ trong tháng.",
            },
        ])

        return components

    def buildRankingSection(self, guild, topMember, rank: int):
        displayName = self.resolveDisplayName(guild, topMember)
        avatarUrl = self.resolveAvatarUrl(guild, topMember.user_id)
        winCount = formatNumber(int(topMember.win_count))

        return {
            "type": DiscordComponentType.SECTION,
            "components": [
                {
                    "type": DiscordComponentType.TEXT_DISPLAY,
                    "content": (
                        f"### #{rank} {displayName}\n"
                        f"{PERFECT} **Số lần thắng:** {winCount}"
                    ),
                },
            ],
            "accessory": {
                "type": DiscordComponentType.THUMBNAIL,
                "media": {
                    "url": avatarUrl,
                },
                "description": displayName,
            },
        }

    def resolveDisplayName(self, guild, topMember):
        guildMember = None

        if guild is not None:
            guildMember = guild.get_member(topMember.user_id)

        if guildMember is not None:
            return guildMember.display_name

        if topMember.nick:
            return topMember.nick

        if topMember.global_name:
            return topMember.global_name

        return topMember.username

    def resolveAvatarUrl(self, guild, userId: int):
        if guild is not None:
            guildMember = guild.get_member(userId)

            if guildMember is not None:
                return guildMember.display_avatar.url

        user = self.bot.get_user(userId)

        if user is not None:
            return user.display_avatar.url

        return self.bot.user.display_avatar.url
