import discord
from discord import app_commands
from discord.ext import commands

from bot.services.partner.createPartnerService import CreatePartnerService


class CreatePartner(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.createPartnerService = CreatePartnerService()

    @app_commands.command(name="createpn", description="Tạo partner mới")
    @app_commands.describe(
        invite_link="Link mời của server partner",
        representative_member="Người đại diện của server partner",
    )
    async def createpn(
        self,
        interaction: discord.Interaction,
        invite_link: str,
        representative_member: discord.Member,
    ):
        if interaction.guild is None:
            await interaction.response.send_message("Lệnh này chỉ dùng được trong server.", ephemeral=True)
            return

        result = await self.createPartnerService.createPartner(
            self.bot,
            interaction,
            invite_link,
            representative_member,
        )

        await interaction.response.send_message(result, ephemeral=True)

async def setup(bot):
    await bot.add_cog(CreatePartner(bot))