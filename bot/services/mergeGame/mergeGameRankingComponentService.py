from discord.http import Route


class MergeGameRankingComponentService:
    COMPONENTS_V2_FLAG = 1 << 15

    def __init__(self, bot):
        self.bot = bot

    async def sendTopMembersMessage(
        self,
        ctx,
        topMembers,
        year: int,
        month: int,
    ):
        payload = {
            "flags": self.COMPONENTS_V2_FLAG,
            "allowed_mentions": {
                "parse": [],
            },
            "components": [
                {
                    "type": 17,
                    "components": self.buildContainerComponents(
                        ctx.guild,
                        topMembers,
                        year,
                        month,
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

    def buildContainerComponents(self, guild, topMembers, year: int, month: int):
        components = [
            {
                "type": 10,
                "content": f"## Merge Game Top 5 - {month:02d}/{year}",
            },
            {
                "type": 14,
            },
        ]

        if not topMembers:
            components.append({
                "type": 10,
                "content": "Chưa có dữ liệu chơi game trong tháng này.",
            })
            return components

        for rank, topMember in enumerate(topMembers, start=1):
            components.append(
                self.buildRankingSection(
                    guild,
                    topMember,
                    rank,
                ),
            )

        return components

    def buildRankingSection(self, guild, topMember, rank: int):
        displayName = self.resolveDisplayName(guild, topMember)
        avatarUrl = self.resolveAvatarUrl(guild, topMember.user_id)
        score = self.formatNumber(topMember.best_score)
        sunTime = self.formatSunTime(topMember.fastest_sun_time)

        return {
            "type": 9,
            "components": [
                {
                    "type": 10,
                    "content": (
                        f"### #{rank} {displayName}\n"
                        f"**Điểm:** {score}\n"
                        f"**Mặt trời nhanh nhất:** {sunTime}"
                    ),
                },
            ],
            "accessory": {
                "type": 11,
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

    def formatNumber(self, value):
        return f"{int(value):,}".replace(",", ".")

    def formatSunTime(self, value):
        if value is None:
            return "--:--"

        totalSeconds = int(value) // 1000
        minutes = totalSeconds // 60
        seconds = totalSeconds % 60

        return f"{minutes:02d}:{seconds:02d}"
