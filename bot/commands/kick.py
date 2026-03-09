import discord
from discord import app_commands
from discord.ext import commands

from bot.config.config import MOD_ADMIN_USER_IDS
from bot.enums.moderationActionType import ModerationActionType
from bot.services.moderation.kickService import KickService
from bot.validation.guildValidation import chillStationOnly
from bot.validation.modChannelValidation import modChannelOnly
from bot.validation.modPermissionValidation import hasModerationPermission


class Kick(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.kickService = KickService()

    @app_commands.command(name="kick", description="Kick một member khỏi server")
    @app_commands.describe(
        target="Member cần kick",
        reason="Lý do kick",
    )
    @chillStationOnly()
    @modChannelOnly()
    @hasModerationPermission(ModerationActionType.KICK)
    async def kick(
        self,
        interaction: discord.Interaction,
        target: discord.Member,
        reason: str,
    ):
        if interaction.guild is None:
            await interaction.response.send_message("Lệnh này chỉ dùng được trong server.")
            return

        if target.id == interaction.user.id:
            await interaction.response.send_message("Bạn không thể kick chính mình.")
            return

        if target.id in MOD_ADMIN_USER_IDS:
            await interaction.response.send_message(
                "Bạn không thể kick member thuộc nhóm quản trị viên được bảo vệ.")
            return

        if target == interaction.guild.owner:
            await interaction.response.send_message("Không thể kick owner của server.")
            return

        if isinstance(interaction.user, discord.Member) and target.top_role >= interaction.user.top_role:
            await interaction.response.send_message(
                "Bạn không thể kick member có role cao hơn hoặc bằng mình.")
            return

        botMember = interaction.guild.get_member(self.bot.user.id)
        if botMember is None or not botMember.guild_permissions.kick_members:
            await interaction.response.send_message("Bot không có quyền kick member.")
            return

        if target.top_role >= botMember.top_role:
            await interaction.response.send_message(
                "Bot không thể kick member có role cao hơn hoặc bằng bot.")
            return

        await interaction.response.defer()

        await target.kick(reason=reason)

        self.kickService.createKickHistory(
            actionByUserId=interaction.user.id,
            targetUserId=target.id,
            reason=reason,
        )

        embed = discord.Embed(
            title="Member đã bị kick",
            description="Hành động moderation đã được thực hiện thành công.",
        )
        embed.add_field(
            name="Người kick",
            value=f"{interaction.user.mention}\n`{interaction.user.id}`",
            inline=False,
        )
        embed.add_field(
            name="Người bị kick",
            value=f"{target.mention}\n`{target.id}`",
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
    await bot.add_cog(Kick(bot))