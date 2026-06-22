import discord
from discord import app_commands
from discord.ext import commands

from bot.config.channel import SHOP_ROLE_CHANNEL_ID
from bot.config.emoji import LOGO
from bot.validation.guildValidation import guildOnly
from bot.validation.isOwnerValidation import isOwner
from bot.views.roleShop.roleShopBuyButtonView import RoleShopBuyButtonView


class CreateRoleShopCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="createroleshop", description="Tạo tin nhắn mua role")
    @app_commands.default_permissions(administrator=True)
    @guildOnly()
    @isOwner()
    async def createRoleShop(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        shopRoleChannel = self.bot.get_channel(SHOP_ROLE_CHANNEL_ID)

        if shopRoleChannel is None:
            try:
                shopRoleChannel = await self.bot.fetch_channel(SHOP_ROLE_CHANNEL_ID)
            except discord.NotFound:
                await interaction.followup.send(
                    f"{LOGO} Không tìm thấy kênh shop role.",
                    ephemeral=True,
                )
                return
            except discord.Forbidden:
                await interaction.followup.send(
                    f"{LOGO} Bot không có quyền xem kênh shop role.",
                    ephemeral=True,
                )
                return
            except discord.HTTPException:
                await interaction.followup.send(
                    f"{LOGO} Không thể lấy thông tin kênh shop role.",
                    ephemeral=True,
                )
                return

        if not isinstance(shopRoleChannel, discord.TextChannel):
            await interaction.followup.send(
                f"{LOGO} SHOP_ROLE_CHANNEL_ID không phải là text channel.",
                ephemeral=True,
            )
            return

        await shopRoleChannel.send(
            f"{LOGO} Vui lòng bấm nút bên dưới để mua role.",
            view=RoleShopBuyButtonView(),
        )

        await interaction.followup.send(
            f"{LOGO} Đã tạo tin nhắn mua role tại {shopRoleChannel.mention}.",
            ephemeral=True,
        )


async def setup(bot):
    bot.add_view(RoleShopBuyButtonView())
    await bot.add_cog(CreateRoleShopCommand(bot))
