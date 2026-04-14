from datetime import timedelta

import discord
from discord import app_commands
from discord.ext import commands

from bot.config.userId import MOD_ADMIN_USER_IDS
from bot.enums.moderationActionType import ModerationActionType
from bot.services.moderation.muteService import MuteService
from bot.validation.guildValidation import chillStationOnly
from bot.validation.modChannelValidation import modChannelOnly
from bot.validation.modPermissionValidation import hasModerationPermission


class Mute(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.muteService = MuteService()

    @app_commands.command(name="mute", description="Mute một member trong server")
    @app_commands.describe(
        target="Member cần mute",
        duration_minutes="Số phút mute",
        reason="Lý do mute",
    )
    @chillStationOnly()
    @modChannelOnly()
    @hasModerationPermission(ModerationActionType.MUTE)
    async def mute(
        self,
        interaction: discord.Interaction,
        target: discord.Member,
        duration_minutes: app_commands.Range[int, 1, 40320],
        reason: str,
    ):
        if interaction.guild is None:
            await interaction.response.send_message("Lệnh này chỉ dùng được trong server.")
            return

        if target.id == interaction.user.id:
            await interaction.response.send_message("Bạn không thể mute chính mình.")
            return

        if target.id in MOD_ADMIN_USER_IDS:
            await interaction.response.send_message(
                "Bạn không thể mute member thuộc nhóm quản trị viên được bảo vệ.")
            return

        if target == interaction.guild.owner:
            await interaction.response.send_message("Không thể mute owner của server.")
            return

        if isinstance(interaction.user, discord.Member) and target.top_role >= interaction.user.top_role:
            await interaction.response.send_message(
                "Bạn không thể mute member có role cao hơn hoặc bằng mình.")
            return

        botMember = interaction.guild.get_member(self.bot.user.id)
        if botMember is None or not botMember.guild_permissions.moderate_members:
            await interaction.response.send_message("Bot không có quyền mute member.")
            return

        if target.top_role >= botMember.top_role:
            await interaction.response.send_message(
                "Bot không thể mute member có role cao hơn hoặc bằng bot.")
            return

        await interaction.response.defer()

        until = discord.utils.utcnow() + timedelta(minutes=duration_minutes)
        await target.timeout(until, reason=reason)

        self.muteService.createMuteHistory(
            actionByUserId=interaction.user.id,
            targetUserId=target.id,
            reason=reason,
            durationMinutes=duration_minutes,
        )

        embed = discord.Embed(
            title="Member đã bị mute",
            description="Hành động moderation đã được thực hiện thành công.",
        )
        embed.add_field(
            name="Người mute",
            value=f"{interaction.user.mention}",
            inline=False,
        )
        embed.add_field(
            name="Người bị mute",
            value=f"{target.mention}",
            inline=False,
        )
        embed.add_field(
            name="Thời lượng",
            value=f"{duration_minutes} phút",
            inline=False,
        )
        embed.add_field(
            name="Lý do",
            value=reason,
            inline=False,
        )

        await interaction.followup.send(
            embed=embed
        )

async def setup(bot):
    await bot.add_cog(Mute(bot))