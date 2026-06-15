import discord
from discord import app_commands
from discord.ext import commands

from bot.config.emoji import LOGO
from bot.services.booster.boosterCustomRoleService import BoosterCustomRoleService
from bot.validation.guildValidation import guildOnly
from bot.validation.isOwnerValidation import isOwner


class SetRoleCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.boosterCustomRoleService = BoosterCustomRoleService()

    @app_commands.command(name="setrole", description="Cấp custom role booster cho member")
    @app_commands.describe(
        user="Member được cấp custom role",
        role="Role custom cần cấp",
    )
    @app_commands.default_permissions(administrator=True)
    @guildOnly()
    @isOwner()
    async def setRole(
        self,
        interaction: discord.Interaction,
        user: discord.Member,
        role: discord.Role,
    ):
        await interaction.response.defer(ephemeral=False)

        result = await self.boosterCustomRoleService.setRole(interaction, user, str(role.id))

        await interaction.followup.send(
            f"{LOGO} {result['message']}",
            ephemeral=False,
        )


async def setup(bot):
    await bot.add_cog(SetRoleCommand(bot))
