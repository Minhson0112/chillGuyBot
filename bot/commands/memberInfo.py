import discord
from discord import app_commands
from discord.ext import commands

from bot.services.member.memberInfoService import MemberInfoService
from bot.validation.guildValidation import chillStationOnly


class MemberInfo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.memberInfoService = MemberInfoService()

    @app_commands.command(name="memberinfo", description="Xem thông tin member")
    @app_commands.describe(target="Member cần xem thông tin")
    @chillStationOnly()
    async def memberInfo(
        self,
        interaction: discord.Interaction,
        target: discord.Member,
    ):
        memberInfo = self.memberInfoService.getMemberInfo(target.id)

        if memberInfo is None:
            await interaction.response.send_message(
                "Không tìm thấy thông tin member trong database.")
            return

        member = memberInfo["member"]
        muteCount = memberInfo["mute_count"]

        dateOfBirth = member.date_of_birth.strftime("%Y-%m-%d") if member.date_of_birth else "Chưa có"
        joinedAt = member.joined_at.strftime("%Y-%m-%d %H:%M:%S") if member.joined_at else "Chưa có"
        nick = member.nick if member.nick else "Không có"
        leaveCount = max(member.join_count - 1, 0)

        embed = discord.Embed(
            title="Thông tin member",
            description=f"Thông tin của {target.mention}",
        )
        embed.add_field(
            name="Tên discord",
            value=member.username,
            inline=False,
        )
        embed.add_field(
            name="Tên trong server Chill Station",
            value=nick,
            inline=False,
        )
        embed.add_field(
            name="Ngày sinh",
            value=dateOfBirth,
            inline=False,
        )
        embed.add_field(
            name="Ngày vào server",
            value=joinedAt,
            inline=False,
        )
        embed.add_field(
            name="Số lần đã out server",
            value=str(leaveCount),
            inline=False,
        )
        embed.add_field(
            name="Số lần bị warning hiện tại",
            value=str(member.warning_count),
            inline=False,
        )
        embed.add_field(
            name="Số lần bị mute",
            value=str(muteCount),
            inline=False,
        )

        avatarUrl = target.display_avatar.url if target.display_avatar else None
        if avatarUrl:
            embed.set_thumbnail(url=avatarUrl)

        await interaction.response.send_message(
            embed=embed
        )


async def setup(bot):
    await bot.add_cog(MemberInfo(bot))