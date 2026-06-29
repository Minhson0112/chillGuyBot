import discord
from discord.ext import commands

from bot.services.farm.farmBaseSkinBuyService import FarmBaseSkinBuyService
from bot.services.farm.farmBaseSkinShopComponentService import FarmBaseSkinShopComponentService


class ShopSkinCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.farmBaseSkinBuyService = FarmBaseSkinBuyService()
        self.farmBaseSkinShopComponentService = FarmBaseSkinShopComponentService(bot)

    @commands.command(name="shopskin")
    async def shopSkin(self, ctx):
        try:
            await self.farmBaseSkinShopComponentService.sendShopMessage(ctx)
        except Exception as e:
            print(f"Show base skin shop error: {e}")
            await ctx.reply("Đã xảy ra lỗi khi mở shop base skin.")

    @commands.Cog.listener()
    async def on_interaction(self, interaction: discord.Interaction):
        if interaction.type != discord.InteractionType.component:
            return

        customId = self.getCustomId(interaction)
        customIdPrefix = self.farmBaseSkinShopComponentService.CUSTOM_ID_PREFIX

        if customId is None or not customId.startswith(f"{customIdPrefix}:"):
            return

        baseSkinIdText = customId.removeprefix(f"{customIdPrefix}:")

        try:
            baseSkinId = int(baseSkinIdText)
        except ValueError:
            await interaction.response.send_message(
                "ID base skin không hợp lệ.",
                ephemeral=True,
            )
            return

        await interaction.response.defer(ephemeral=True)

        try:
            result = self.farmBaseSkinBuyService.buyBaseSkin(
                userId=interaction.user.id,
                baseSkinId=baseSkinId,
            )

            await interaction.followup.send(
                result["message"],
                ephemeral=True,
            )
        except Exception as e:
            print(f"Buy base skin from shop error: {e}")
            await interaction.followup.send(
                "Đã xảy ra lỗi khi mua base skin.",
                ephemeral=True,
            )

    def getCustomId(self, interaction: discord.Interaction):
        if interaction.data is None:
            return None

        return interaction.data.get("custom_id")


async def setup(bot):
    await bot.add_cog(ShopSkinCommand(bot))
