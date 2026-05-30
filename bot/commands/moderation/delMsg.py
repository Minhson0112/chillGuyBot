import discord
from discord import app_commands
from discord.ext import commands

from bot.enums.moderationActionType import ModerationActionType
from bot.validation.guildValidation import chillStationOnly
from bot.validation.modPermissionValidation import hasModerationPermission


class DelMessage(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="delmsg", description="Xóa một số lượng tin nhắn trong kênh hiện tại")
    @app_commands.describe(
        amount="Số lượng tin nhắn cần xóa",
    )
    @chillStationOnly()
    @hasModerationPermission(ModerationActionType.DELMSG)
    async def delmsg(
        self,
        interaction: discord.Interaction,
        amount: app_commands.Range[int, 1, 300],
    ):
        if interaction.guild is None:
            await interaction.response.send_message("Lệnh này chỉ dùng được trong server.")
            return

        if not isinstance(interaction.channel, discord.TextChannel):
            await interaction.response.send_message("Kênh hiện tại không hỗ trợ xóa tin nhắn kiểu này.")
            return

        botMember = interaction.guild.get_member(self.bot.user.id)
        if botMember is None or not botMember.guild_permissions.manage_messages:
            await interaction.response.send_message("Bot không có quyền xóa tin nhắn.")
            return

        if interaction.channel.permissions_for(botMember).manage_messages is False:
            await interaction.response.send_message("Bot không có quyền xóa tin nhắn trong kênh này.")
            return

        await interaction.response.defer(ephemeral=True)

        deletedMessages = await interaction.channel.purge(limit=amount)

        await interaction.followup.send(
            f"Đã xóa {len(deletedMessages)} tin nhắn trong kênh này.",
            ephemeral=True,
        )


async def setup(bot):
    await bot.add_cog(DelMessage(bot))