from datetime import datetime, timedelta, timezone

from discord.http import Route

from bot.config.database import getDbSession
from bot.config.emoji import SATURN, SUN
from bot.enums.discordComponentType import DiscordComponentType
from bot.helper.numberFormatHelper import formatNumber
from bot.helper.timeFormatHelper import formatMillisecondsMinutesSeconds
from bot.repository.mergeGamePlayHistoryRepository import MergeGamePlayHistoryRepository


class MergeGameRankingComponentService:
    COMPONENTS_V2_FLAG = 1 << 15
    RANKING_TYPE_SCORE = "score"
    RANKING_TYPE_SUN = "sun"
    CUSTOM_ID_PREFIX = "mergeverse_top"
    SCORE_RANKING_EMOJI = SATURN
    SUN_RANKING_EMOJI = SUN

    def __init__(self, bot):
        self.bot = bot
        self.gmt7 = timezone(timedelta(hours=7))

    async def sendTopMembersMessage(
        self,
        ctx,
        rankingType: str = RANKING_TYPE_SCORE,
    ):
        topMembers, targetYear, targetMonth = self.findTopMembers(rankingType)
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
                        rankingType,
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

    async def updateTopMembersMessage(
        self,
        interaction,
        rankingType: str,
    ):
        topMembers, targetYear, targetMonth = self.findTopMembers(rankingType)
        payload = {
            "allowed_mentions": {
                "parse": [],
            },
            "components": [
                {
                    "type": DiscordComponentType.CONTAINER,
                    "components": self.buildContainerComponents(
                        interaction.guild,
                        topMembers,
                        targetYear,
                        targetMonth,
                        rankingType,
                    ),
                },
            ],
        }

        await self.bot.http.request(
            Route(
                "PATCH",
                "/channels/{channel_id}/messages/{message_id}",
                channel_id=interaction.channel.id,
                message_id=interaction.message.id,
            ),
            json=payload,
        )

    def findTopMembers(self, rankingType: str):
        nowGmt7 = datetime.now(self.gmt7)
        targetYear = nowGmt7.year
        targetMonth = nowGmt7.month

        with getDbSession() as session:
            mergeGamePlayHistoryRepository = MergeGamePlayHistoryRepository(session)

            if rankingType == self.RANKING_TYPE_SUN:
                topMembers = mergeGamePlayHistoryRepository.findTopSunMembersByMonth(
                    targetYear,
                    targetMonth,
                    5,
                )
            else:
                topMembers = mergeGamePlayHistoryRepository.findTopMembersByMonth(
                    targetYear,
                    targetMonth,
                    5,
                )

        return topMembers, targetYear, targetMonth

    def buildContainerComponents(
        self,
        guild,
        topMembers,
        year: int,
        month: int,
        rankingType: str,
    ):
        components = [
            {
                "type": DiscordComponentType.TEXT_DISPLAY,
                "content": f"## Mergeverse Game Top 5 - {month:02d}/{year}",
            },
            {
                "type": DiscordComponentType.SEPARATOR,
            },
        ]

        if not topMembers:
            components.append({
                "type": DiscordComponentType.TEXT_DISPLAY,
                "content": self.buildEmptyMessage(rankingType),
            })
            return self.appendFooterComponents(components, rankingType)

        for rank, topMember in enumerate(topMembers, start=1):
            components.append(
                self.buildRankingSection(
                    guild,
                    topMember,
                    rank,
                ),
            )

        return self.appendFooterComponents(components, rankingType)

    def appendFooterComponents(self, components, rankingType: str):
        components.extend([
            {
                "type": DiscordComponentType.SEPARATOR,
            },
            {
                "type": DiscordComponentType.ACTION_ROW,
                "components": [
                    {
                        "type": DiscordComponentType.BUTTON,
                        "style": self.getButtonStyle(self.RANKING_TYPE_SCORE, rankingType),
                        "label": "Top điểm",
                        "emoji": self.buildEmojiPayload(self.SCORE_RANKING_EMOJI),
                        "custom_id": self.buildCustomId(self.RANKING_TYPE_SCORE),
                    },
                    {
                        "type": DiscordComponentType.BUTTON,
                        "style": self.getButtonStyle(self.RANKING_TYPE_SUN, rankingType),
                        "label": "Top mặt trời",
                        "emoji": self.buildEmojiPayload(self.SUN_RANKING_EMOJI),
                        "custom_id": self.buildCustomId(self.RANKING_TYPE_SUN),
                    },
                ],
            },
            {
                "type": DiscordComponentType.TEXT_DISPLAY,
                "content": f"-# {self.getRankingLabel(rankingType)} | dùng `cg mymerge` để xem điểm của bạn.",
            },
        ])

        return components

    def buildRankingSection(self, guild, topMember, rank: int):
        displayName = self.resolveDisplayName(guild, topMember)
        avatarUrl = self.resolveAvatarUrl(guild, topMember.user_id)
        score = formatNumber(int(topMember.best_score))
        sunTime = formatMillisecondsMinutesSeconds(topMember.fastest_sun_time)

        return {
            "type": DiscordComponentType.SECTION,
            "components": [
                {
                    "type": DiscordComponentType.TEXT_DISPLAY,
                    "content": (
                        f"### #{rank} {displayName}\n"
                        f"{SATURN} **Điểm:** {score}\n"
                        f"{SUN} **Mặt trời nhanh nhất:** {sunTime}"
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

    def buildEmptyMessage(self, rankingType: str):
        if rankingType == self.RANKING_TYPE_SUN:
            return "Chưa có dữ liệu tạo mặt trời trong tháng này."

        return "Chưa có dữ liệu chơi game trong tháng này."

    def buildCustomId(self, rankingType: str):
        return f"{self.CUSTOM_ID_PREFIX}:{rankingType}"

    def getButtonStyle(self, buttonRankingType: str, currentRankingType: str):
        if buttonRankingType == currentRankingType:
            return 1

        return 2

    def getRankingLabel(self, rankingType: str):
        if rankingType == self.RANKING_TYPE_SUN:
            return "Top mặt trời"

        return "Top điểm"

    def buildEmojiPayload(self, emoji: str):
        emojiParts = emoji.strip("<>").split(":")

        if len(emojiParts) == 3:
            return {
                "name": emojiParts[1],
                "id": emojiParts[2],
                "animated": emojiParts[0] == "a",
            }

        return {
            "name": emoji,
        }
