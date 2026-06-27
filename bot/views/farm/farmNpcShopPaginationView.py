import discord

from bot.services.farm.farmShopRenderService import FarmShopRenderService


class FarmNpcShopPaginationView(discord.ui.View):
    GUIDE_TEXT = (
        "Để mua đồ hãy dùng lệnh: `cg buy {id đồ} {số lượng muốn mua}`\n"
        "Nếu không nhập số lượng thì mặc định là **1**.\n"
        "Để xem thông tin đồ hãy dùng lệnh `cg info {id đồ}`"
    )
    def __init__(
        self,
        authorId: int,
        currentPage: int,
        totalPage: int,
    ):
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
        await interaction.response.defer()

        renderResult = self.farmShopRenderService.renderShopPageToBuffer(
            page=self.currentPage,
        )

        self.currentPage = renderResult["currentPage"]
        self.totalPage = renderResult["totalPage"]

        self.updateButtonState()

        file = discord.File(
            renderResult["buffer"],
            filename="farm_shop.png",
        )

        await interaction.edit_original_response(
            content=self.GUIDE_TEXT,
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

    @discord.ui.button(label="Hướng dẫn", emoji="📖", style=discord.ButtonStyle.primary)
    async def refreshButton(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.updateShopMessage(interaction)

    @discord.ui.button(label="Trước", emoji="⬅️", style=discord.ButtonStyle.secondary)
    async def previousButton(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.currentPage > 1:
            self.currentPage -= 1

        await self.updateShopMessage(interaction)

    @discord.ui.button(label="Tiếp", emoji="➡️", style=discord.ButtonStyle.secondary)
    async def nextButton(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.currentPage < self.totalPage:
            self.currentPage += 1

        await self.updateShopMessage(interaction)
