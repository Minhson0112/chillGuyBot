import discord
from discord import app_commands
from discord.ext import commands

from bot.services.autoResponder.showAllAutoResponseService import ShowAllAutoResponseService
from bot.validation.guildValidation import chillStationOnly
from bot.views.autoResponder.autoResponderPaginationView import AutoResponderPaginationView


class ShowAllAutoResponse(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.showAllAutoResponseService = ShowAllAutoResponseService()

    @app_commands.command(name="showallautoresponse", description="Hiển thị toàn bộ auto response")
    @chillStationOnly()
    async def showAllAutoResponse(self, interaction: discord.Interaction):
        if not self.showAllAutoResponseService.canShowAllAutoResponse(interaction.user.id):
            await interaction.response.send_message("Bạn không có quyền dùng lệnh này.")
            return

        autoResponders = self.showAllAutoResponseService.getAllAutoResponders()

        view = AutoResponderPaginationView(autoResponders, perPage=5)
        embed = view.buildEmbed()

        await interaction.response.send_message(embed=embed, view=view)


async def setup(bot):
    await bot.add_cog(ShowAllAutoResponse(bot))
