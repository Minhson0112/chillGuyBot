import discord
from discord.ext import commands

from bot.services.farm.farmShopRenderService import FarmShopRenderService


class FarmShopPaginationView(discord.ui.View):
    def __init__(self, authorId: int, currentPage: int, totalPage: int):
        super().__init__(timeout=180)

        self.authorId = authorId
        self.currentPage = currentPage
        self.totalPage = totalPage
        self.farmShopRenderService = FarmShopRenderService()

        self.updateButtonState()

    def updateButtonState(self):
        self.previousButton.disabled = self.currentPage <= 1
        self.nextButton.disabled = self.currentPage >= self.totalPage

    async def updateShopMessage(self, interaction: discord.Interaction):
        renderResult = self.farmShopRenderService.renderShopPageToBuffer(self.currentPage)

        self.currentPage = renderResult["currentPage"]
        self.totalPage = renderResult["totalPage"]

        self.updateButtonState()

        file = discord.File(
            renderResult["buffer"],
            filename="farm_shop.png",
        )

        await interaction.response.edit_message(
            attachments=[file],
            view=self,
        )

    async def interaction_check(self, interaction: discord.Interaction):
        if interaction.user.id != self.authorId:
            await interaction.response.send_message(
                "Bạn không thể điều khiển shop của người khác.",
                ephemeral=True,
            )
            return False

        return True

    @discord.ui.button(label="Trước", style=discord.ButtonStyle.secondary)
    async def previousButton(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.currentPage -= 1
        await self.updateShopMessage(interaction)

    @discord.ui.button(label="Tiếp", style=discord.ButtonStyle.secondary)
    async def nextButton(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.currentPage += 1
        await self.updateShopMessage(interaction)


class ShopFarmCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.farmShopRenderService = FarmShopRenderService()

    @commands.command(name="shopfarm")
    async def shopFarm(self, ctx, page: int = 1):
        try:
            renderResult = self.farmShopRenderService.renderShopPageToBuffer(page)

            file = discord.File(
                renderResult["buffer"],
                filename="farm_shop.png",
            )

            view = FarmShopPaginationView(
                authorId=ctx.author.id,
                currentPage=renderResult["currentPage"],
                totalPage=renderResult["totalPage"],
            )

            await ctx.reply(file=file, view=view)

        except FileNotFoundError as e:
            print(f"Farm shop asset file not found: {e}")
            await ctx.reply("Không tìm thấy ảnh asset để render shop.")

        except Exception as e:
            print(f"Render farm shop error: {e}")
            await ctx.reply("Đã xảy ra lỗi khi render shop.")


async def setup(bot):
    await bot.add_cog(ShopFarmCommand(bot))