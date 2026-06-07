import discord
from discord import app_commands
from discord.ext import commands

from bot.services.server.serverInviteSyncService import ServerInviteSyncService
from bot.validation.guildValidation import chillStationOnly


class SyncInvitesCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.serverInviteSyncService = ServerInviteSyncService()

    @app_commands.command(
        name="syncinvites",
        description="Fetch và đồng bộ invite hiện tại của server vào database",
    )
    @app_commands.default_permissions(manage_guild=True)
    @chillStationOnly()
    async def syncInvites(self, interaction: discord.Interaction):
        member = interaction.user

        if not isinstance(member, discord.Member):
            raise app_commands.CheckFailure("Không xác định được member trong server.")

        if not member.guild_permissions.manage_guild:
            raise app_commands.CheckFailure("Bạn cần quyền quản lý server để sử dụng lệnh này.")

        await interaction.response.defer(ephemeral=True)

        try:
            syncResult = await self.serverInviteSyncService.syncGuildInvites(interaction.guild)
        except discord.Forbidden:
            await interaction.followup.send(
                "Bot không có quyền fetch invite của server. Vui lòng kiểm tra quyền Manage Server.",
                ephemeral=True,
            )
            return
        except discord.HTTPException as e:
            await interaction.followup.send(
                f"Fetch invite thất bại do lỗi Discord: {e}",
                ephemeral=True,
            )
            return

        await interaction.followup.send(
            "Server invite sync job fetched "
            f"{syncResult['fetchedCount']} invites, "
            f"created {syncResult['createdCount']}, "
            f"updated {syncResult['updatedCount']}, "
            f"unchanged {syncResult['unchangedCount']}",
            ephemeral=True,
        )


async def setup(bot):
    await bot.add_cog(SyncInvitesCommand(bot))
