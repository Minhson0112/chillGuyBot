from datetime import datetime, timedelta, timezone

import discord

from bot.config.database import getDbSession
from bot.config.channel import BIRTHDAY_CHANNEL_ID
from bot.repository.memberRepository import MemberRepository


class MemberBirthdayAnnounceService:
    def __init__(self, bot):
        self.bot = bot
        self.gmt7 = timezone(timedelta(hours=7))

    async def sendTodayBirthdayMessages(self):
        nowGmt7 = datetime.now(self.gmt7)
        month = nowGmt7.month
        day = nowGmt7.day

        with getDbSession() as session:
            memberRepository = MemberRepository(session)
            birthdayMembers = memberRepository.findMembersByBirthday(month, day)

        if not birthdayMembers:
            return

        channel = self.bot.get_channel(BIRTHDAY_CHANNEL_ID)

        if channel is None:
            channel = await self.bot.fetch_channel(BIRTHDAY_CHANNEL_ID)

        guild = channel.guild
        dateText = nowGmt7.strftime("%d-%m-%Y")

        for birthdayMember in birthdayMembers:
            discordMember = guild.get_member(birthdayMember.user_id)

            if discordMember is None:
                try:
                    discordMember = await guild.fetch_member(birthdayMember.user_id)
                except discord.NotFound:
                    continue
                except discord.HTTPException:
                    continue

            age = nowGmt7.year - birthdayMember.date_of_birth.year
            embed = self.buildBirthdayEmbed(discordMember, birthdayMember, age, dateText)

            await channel.send(
                content=discordMember.mention,
                embed=embed,
            )

    def buildBirthdayEmbed(self, discordMember, birthdayMember, age: int, dateText: str):
        displayName = discordMember.display_name
        avatarUrl = discordMember.display_avatar.url

        embed = discord.Embed(
            title="Happy Birthday",
            description=f"Chúc mừng {discordMember.mention} đã bước sang tuổi mới.",
            color=discord.Color.purple(),
        )

        embed.set_author(
            name=displayName,
            icon_url=avatarUrl,
        )
        embed.set_thumbnail(url=avatarUrl)

        embed.add_field(
            name="Lời chúc",
            value=(
                f"<a:CS_decorate:1366286341284827156> {discordMember.mention} ơi hôm nay bạn đã tròn **{age} tuổi** rùi đó.\n"
                f"<a:CS_giveaway:1466240628240285916> Chúc bạn luôn vui vẻ, mạnh khỏe, gặp nhiều may mắn "
                f"và có những khoảnh khắc thật nhiều niềm vui cùng Chill Station."
            ),
            inline=False,
        )

        embed.set_footer(text="Chill Station Birthday Celebration")

        return embed