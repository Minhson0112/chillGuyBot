import discord
from discord import app_commands
from discord.ext import commands

from bot.services.member.memberAutoResponderPermissionService import MemberAutoResponderPermissionService


class SetAutoRes(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.memberAutoResponderPermissionService = MemberAutoResponderPermissionService()

    @app_commands.command(
        name="setautores",
        description="Set auto responder permission for a member",
    )
    @app_commands.describe(
        target="Member cần cấp quyền tạo auto response",
    )
    async def setAutoRes(
        self,
        interaction: discord.Interaction,
        target: discord.Member,
    ):
        await interaction.response.defer(ephemeral=False)

        result = await self.memberAutoResponderPermissionService.setAutoResponderPermission(
            interaction,
            target,
        )

        await interaction.followup.send(
            result["message"],
            ephemeral=False,
        )


async def setup(bot):
    await bot.add_cog(SetAutoRes(bot))