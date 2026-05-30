import discord
from discord import app_commands
from discord.ext import commands

from bot.services.member.memberSyncService import MemberSyncService
from bot.validation.guildValidation import chillStationOnly


class LoadMember(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.memberSyncService = MemberSyncService()

    @app_commands.command(name="loadmember", description="Load all current guild members into database")
    @chillStationOnly()
    async def loadMember(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        syncedCount = self.memberSyncService.syncGuildMembers(interaction.guild)

        await interaction.followup.send(
            f"Đã lưu hoặc cập nhật {syncedCount} member vào database.",
            ephemeral=True
        )


async def setup(bot):
    await bot.add_cog(LoadMember(bot))