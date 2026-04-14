import discord
from discord import app_commands
from discord.ext import commands

from bot.config.userId import MOD_ADMIN_USER_IDS
from bot.enums.moderationActionType import ModerationActionType
from bot.services.moderation.banService import BanService
from bot.validation.guildValidation import chillStationOnly
from bot.validation.modChannelValidation import modChannelOnly
from bot.validation.modPermissionValidation import hasModerationPermission

class Ban(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.banService = BanService()

    @app_commands.command(name="ban", description="Ban một member khỏi server")
    @app_commands.describe(
        target="Member cần ban",
        reason="Lý do ban",
    )
    @chillStationOnly()
    @modChannelOnly()
    @hasModerationPermission(ModerationActionType.BAN)
    async def ban(
        self,
        interaction: discord.Interaction,
        target: discord.Member,
        reason: str,
    ):
        if interaction.guild is None:
            await interaction.response.send_message("Lệnh này chỉ dùng được trong server.")
            return

        if target.id == interaction.user.id:
            await interaction.response.send_message("Bạn không thể ban chính mình.")
            return

        if target == interaction.guild.owner:
            await interaction.response.send_message("Không thể ban owner của server.")
            return

        if target.id in MOD_ADMIN_USER_IDS:
            await interaction.response.send_message("Bạn không thể kick member thuộc nhóm quản trị viên được bảo vệ.")
            return

        if isinstance(interaction.user, discord.Member) and target.top_role >= interaction.user.top_role:
            await interaction.response.send_message("Bạn không thể ban member có role cao hơn hoặc bằng mình.")
            return

        botMember = interaction.guild.get_member(self.bot.user.id)
        if botMember is None or not botMember.guild_permissions.ban_members:
            await interaction.response.send_message("Bot không có quyền ban member.")
            return

        if botMember is not None and target.top_role >= botMember.top_role:
            await interaction.response.send_message("Bot không thể ban member có role cao hơn hoặc bằng bot.")
            return

        await interaction.response.defer()

        await interaction.guild.ban(target, reason=reason, delete_message_seconds=0)

        self.banService.createBanHistory(
            actionByUserId=interaction.user.id,
            targetUserId=target.id,
            reason=reason,
        )

        embed = discord.Embed(
            title="Member đã bị ban",
            description="Hành động moderation đã được thực hiện thành công.",
        )

        embed.add_field(
            name="Người ban",
            value=interaction.user.mention,
            inline=False,
        )
        embed.add_field(
            name="Người bị ban",
            value=f"{target.mention}",
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
    await bot.add_cog(Ban(bot))