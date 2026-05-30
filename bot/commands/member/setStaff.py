import discord
from discord import app_commands
from discord.ext import commands

from bot.services.member.memberStaffService import MemberStaffService


class SetStaff(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.memberStaffService = MemberStaffService()

    @app_commands.command(
        name="setstaff",
        description="Set staff permission for a member",
    )
    @app_commands.describe(
        target="Member cần set staff",
    )
    async def setStaff(
        self,
        interaction: discord.Interaction,
        target: discord.Member,
    ):
        await interaction.response.defer(ephemeral=False)

        result = await self.memberStaffService.setStaff(interaction, target)

        await interaction.followup.send(
            result["message"],
            ephemeral=False,
        )


async def setup(bot):
    await bot.add_cog(SetStaff(bot))