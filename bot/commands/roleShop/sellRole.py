import discord
from discord import app_commands
from discord.ext import commands

from bot.config.emoji import LOGO
from bot.services.roleShop.roleShopService import RoleShopService
from bot.validation.isOwnerValidation import isOwner
from bot.validation.guildValidation import guildOnly


class SellRoleCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.roleShopService = RoleShopService()

    @app_commands.command(name="sellrole", description="Thêm role vào shop bán role")
    @app_commands.default_permissions(administrator=True)
    @app_commands.describe(
        role_id="ID của role Discord",
        price_owo="Giá bán bằng cowoncy",
        price_chill_coin="Giá bán bằng chill coin",
    )
    @guildOnly()
    @isOwner()
    async def sellRole(
        self,
        interaction: discord.Interaction,
        role_id: str,
        price_owo: int,
        price_chill_coin: int,
    ):
        await interaction.response.defer(ephemeral=True)

        if not role_id.isdigit():
            await interaction.followup.send(f"Role ID không hợp lệ.")
            return

        roleId = int(role_id)
        role = interaction.guild.get_role(roleId)

        if role is None:
            await interaction.followup.send(f"Không tìm thấy role trong server này.")
            return

        result = self.roleShopService.createSellRole(
            roleId=roleId,
            priceCowoncy=price_owo,
            priceChillCoin=price_chill_coin,
        )

        if not result["success"]:
            await interaction.followup.send(f"{result['message']}")
            return

        await interaction.followup.send(
            f"{LOGO} {result['message']}\n"
            f"Role: {role.mention}\n"
            f"Giá cowoncy: **{price_owo:,}**\n"
            f"Giá chill coin: **{price_chill_coin:,}**\n"
            f"Thời hạn: **30 ngày**"
        )


async def setup(bot):
    await bot.add_cog(SellRoleCommand(bot))
