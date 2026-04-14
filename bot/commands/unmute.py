import discord
from discord import app_commands
from discord.ext import commands

from bot.config.userId import MOD_ADMIN_USER_IDS
from bot.enums.moderationActionType import ModerationActionType
from bot.services.moderation.unmuteService import UnmuteService
from bot.validation.guildValidation import chillStationOnly
from bot.validation.modChannelValidation import modChannelOnly
from bot.validation.modPermissionValidation import hasModerationPermission


class Unmute(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.unmuteService = UnmuteService()

    @app_commands.command(name="unmute", description="Bỏ mute một member trong server")
    @app_commands.describe(
        target="Member cần bỏ mute",
    )
    @chillStationOnly()
    @modChannelOnly()
    @hasModerationPermission(ModerationActionType.UNMUTE)
    async def unmute(
        self,
        interaction: discord.Interaction,
        target: discord.Member,
    ):
        if interaction.guild is None:
            await interaction.response.send_message("Lệnh này chỉ dùng được trong server.")
            return

        if target.id == interaction.user.id:
            await interaction.response.send_message("Bạn không thể tự unmute chính mình.")
            return

        if target.id in MOD_ADMIN_USER_IDS:
            await interaction.response.send_message(
                "Bạn không thể unmute member thuộc nhóm quản trị viên được bảo vệ."
            )
            return

        if target == interaction.guild.owner:
            await interaction.response.send_message("Không thể unmute owner của server.")
            return

        if isinstance(interaction.user, discord.Member) and target.top_role >= interaction.user.top_role:
            await interaction.response.send_message(
                "Bạn không thể unmute member có role cao hơn hoặc bằng mình."
            )
            return

        botMember = interaction.guild.get_member(self.bot.user.id)
        if botMember is None or not botMember.guild_permissions.moderate_members:
            await interaction.response.send_message("Bot không có quyền unmute member.")
            return

        if target.top_role >= botMember.top_role:
            await interaction.response.send_message(
                "Bot không thể unmute member có role cao hơn hoặc bằng bot."
            )
            return

        if target.timed_out_until is None:
            await interaction.response.send_message("Member này hiện không bị mute.")
            return

        await interaction.response.defer()

        await target.timeout(None, reason=f"Unmuted by {interaction.user}.")

        self.unmuteService.createUnmuteHistory(
            actionByUserId=interaction.user.id,
            targetUserId=target.id,
        )

        embed = discord.Embed(
            title="Member đã được unmute",
            description="Hành động moderation đã được thực hiện thành công.",
        )
        embed.add_field(
            name="Người unmute",
            value=f"{interaction.user.mention}",
            inline=False,
        )
        embed.add_field(
            name="Người được unmute",
            value=f"{target.mention}",
            inline=False,
        )

        await interaction.followup.send(
            embed=embed
        )


async def setup(bot):
    await bot.add_cog(Unmute(bot))