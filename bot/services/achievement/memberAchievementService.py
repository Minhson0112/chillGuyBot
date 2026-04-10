from datetime import datetime, timedelta, timezone

import discord

from bot.config.config import ACHIEVEMENTS_CHANNEL_ID
from bot.config.config import LOGO
from bot.services.achievement.achievementImageService import AchievementImageService


class MemberAchievementService:
    def __init__(self):
        self.achievementImageService = AchievementImageService()
        self.gmt7 = timezone(timedelta(hours=7))

    async def handleMemberMilestone(self, guild: discord.Guild):
        memberCount = guild.member_count or len(guild.members)

        if memberCount % 100 != 0:
            return

        onlineCount = sum(
            1 for member in guild.members
            if member.status != discord.Status.offline
        )

        buffer = self.achievementImageService.buildAchievementImage(
            onlineCount=onlineCount,
            memberCount=memberCount,
        )

        channel = guild.get_channel(ACHIEVEMENTS_CHANNEL_ID)
        if channel is None:
            channel = await guild.fetch_channel(ACHIEVEMENTS_CHANNEL_ID)

        nowGmt7 = datetime.now(self.gmt7)
        dateText = nowGmt7.strftime("%d/%m/%Y")

        message = (
            f"# <a:CS_giveaway:1466240628240285916> Chúc mừng {LOGO} đã đạt mốc **{memberCount:,} thành viên**\n"
            f"Thời gian: **{dateText}**"
        )

        file = discord.File(buffer, filename="achievement.png")
        await channel.send(content=message, file=file)