import discord
from discord import app_commands
from discord.ext import commands

from bot.services.member.memberModService import MemberModService


class SetMod(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.memberModService = MemberModService()

    @app_commands.command(
        name="setmod",
        description="Set mod permission for a member",
    )
    @app_commands.describe(
        target="Member cần set mod",
    )
    async def setMod(
        self,
        interaction: discord.Interaction,
        target: discord.Member,
    ):
        await interaction.response.defer(ephemeral=False)

        result = await self.memberModService.setMod(interaction, target)

        await interaction.followup.send(
            result["message"],
            ephemeral=False,
        )


async def setup(bot):
    await bot.add_cog(SetMod(bot))