import discord
from discord import app_commands
from discord.ext import commands

from bot.config.emoji import LOGO
from bot.services.serverItem.coupleRoleService import CoupleRoleService
from bot.validation.guildValidation import guildOnly
from bot.validation.isOwnerValidation import isOwner


class SetCoupleRoleCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.coupleRoleService = CoupleRoleService()

    @app_commands.command(name="setcouplerole", description="Cấp role cho một couple và lưu role vào database")
    @app_commands.describe(
        user1="Member thứ nhất trong couple",
        user2="Member thứ hai trong couple",
        role="Role couple cần cấp",
    )
    @app_commands.default_permissions(administrator=True)
    @guildOnly()
    @isOwner()
    async def setCoupleRole(
        self,
        interaction: discord.Interaction,
        user1: discord.Member,
        user2: discord.Member,
        role: discord.Role,
    ):
        await interaction.response.defer(ephemeral=False)

        result = await self.coupleRoleService.setCoupleRole(
            guild=interaction.guild,
            user1=user1,
            user2=user2,
            role=role,
        )

        await interaction.followup.send(
            f"{LOGO} {result['message']}",
            ephemeral=False,
        )


async def setup(bot):
    await bot.add_cog(SetCoupleRoleCommand(bot))
