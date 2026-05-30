import discord
from discord import app_commands
from discord.ext import commands

from bot.services.member.memberAdminService import MemberAdminService


class RemoveAdmin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.memberAdminService = MemberAdminService()

    @app_commands.command(
        name="removeadmin",
        description="Remove admin permission from a member",
    )
    @app_commands.describe(
        target="Member cần gỡ admin",
    )
    async def removeAdmin(
        self,
        interaction: discord.Interaction,
        target: discord.Member,
    ):
        await interaction.response.defer(ephemeral=False)

        result = await self.memberAdminService.removeAdmin(interaction, target)

        await interaction.followup.send(
            result["message"],
            ephemeral=False,
        )


async def setup(bot):
    await bot.add_cog(RemoveAdmin(bot))