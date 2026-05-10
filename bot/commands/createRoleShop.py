import discord
from discord import app_commands
from discord.ext import commands

from bot.config.emoji import LOGO
from bot.views.roleShopBuyButtonView import RoleShopBuyButtonView
from bot.validation.isOwnerValidation import isOwner
from bot.validation.guildValidation import guildOnly


class CreateRoleShopCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="createroleshop", description="Tạo tin nhắn mua role")
    @app_commands.default_permissions(administrator=True)
    @guildOnly()
    @isOwner()
    async def createRoleShop(self, interaction: discord.Interaction):

        await interaction.response.send_message(
            f"{LOGO} Vui lòng bấm nút bên dưới để mua role.",
            view=RoleShopBuyButtonView(),
        )


async def setup(bot):
    bot.add_view(RoleShopBuyButtonView())
    await bot.add_cog(CreateRoleShopCommand(bot))