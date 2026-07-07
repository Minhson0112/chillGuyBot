import discord
from discord.ext import commands

from bot.services.serverItem.serverItemShopMessageService import ServerItemShopMessageService
from bot.views.serverItem.loveShopQuantityModal import LoveShopQuantityModal


class LoveShopCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.serverItemShopMessageService = ServerItemShopMessageService()

    @commands.command(name="loveshop")
    async def loveShop(self, ctx):
        try:
            await self.serverItemShopMessageService.sendShopMessage(ctx)
        except Exception as e:
            print(f"Show love shop error: {e}")
            await ctx.reply("Đã xảy ra lỗi khi mở love shop.")

    @commands.Cog.listener()
    async def on_interaction(self, interaction: discord.Interaction):
        if interaction.type != discord.InteractionType.component:
            return

        customId = self.getCustomId(interaction)
        customIdPrefix = self.serverItemShopMessageService.CUSTOM_ID_PREFIX

        if customId is None or not customId.startswith(f"{customIdPrefix}:"):
            return

        itemIdText = customId.removeprefix(f"{customIdPrefix}:")

        try:
            itemId = int(itemIdText)
        except ValueError:
            await interaction.response.send_message(
                "ID item không hợp lệ.",
                ephemeral=True,
            )
            return

        if interaction.guild is None:
            await interaction.response.send_message(
                "Lệnh mua item love shop chỉ dùng được trong server.",
                ephemeral=True,
            )
            return

        await interaction.response.send_modal(LoveShopQuantityModal(itemId))

    def getCustomId(self, interaction: discord.Interaction):
        if interaction.data is None:
            return None

        return interaction.data.get("custom_id")


async def setup(bot):
    await bot.add_cog(LoveShopCommand(bot))
