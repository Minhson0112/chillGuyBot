import discord
from discord import app_commands
from discord.ext import commands

from bot.services.member.memberAdminService import MemberAdminService


class SetAdmin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.memberAdminService = MemberAdminService()

    @app_commands.command(
        name="setadmin",
        description="Set admin permission for a member",
    )
    @app_commands.describe(
        target="Member cần set admin",
    )
    async def setAdmin(
        self,
        interaction: discord.Interaction,
        target: discord.Member,
    ):
        await interaction.response.defer(ephemeral=False)

        result = await self.memberAdminService.setAdmin(interaction, target)

        await interaction.followup.send(
            result["message"],
            ephemeral=False,
        )


async def setup(bot):
    await bot.add_cog(SetAdmin(bot))