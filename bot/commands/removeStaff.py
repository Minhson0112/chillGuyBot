import discord
from discord import app_commands
from discord.ext import commands

from bot.services.member.memberStaffService import MemberStaffService


class RemoveStaff(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.memberStaffService = MemberStaffService()

    @app_commands.command(
        name="removestaff",
        description="Remove staff permission from a member",
    )
    @app_commands.describe(
        target="Member cần gỡ staff",
    )
    async def removeStaff(
        self,
        interaction: discord.Interaction,
        target: discord.Member,
    ):
        await interaction.response.defer(ephemeral=False)

        result = await self.memberStaffService.removeStaff(interaction, target)

        await interaction.followup.send(
            result["message"],
            ephemeral=False,
        )


async def setup(bot):
    await bot.add_cog(RemoveStaff(bot))