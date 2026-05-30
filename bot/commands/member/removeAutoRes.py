import discord
from discord import app_commands
from discord.ext import commands

from bot.services.member.memberAutoResponderPermissionService import MemberAutoResponderPermissionService


class RemoveAutoRes(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.memberAutoResponderPermissionService = MemberAutoResponderPermissionService()

    @app_commands.command(
        name="removeautores",
        description="Remove auto responder permission from a member",
    )
    @app_commands.describe(
        target="Member cần xóa quyền tạo auto response",
    )
    async def removeAutoRes(
        self,
        interaction: discord.Interaction,
        target: discord.Member,
    ):
        await interaction.response.defer(ephemeral=False)

        result = await self.memberAutoResponderPermissionService.removeAutoResponderPermission(
            interaction,
            target,
        )

        await interaction.followup.send(
            result["message"],
            ephemeral=False,
        )


async def setup(bot):
    await bot.add_cog(RemoveAutoRes(bot))