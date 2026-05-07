import discord

from bot.services.farm.farmRecipeRenderService import FarmRecipeRenderService


class FarmRecipePaginationView(discord.ui.View):
    COOK_GUIDE_TEXT = (
        "Để nấu ăn hãy dùng lệnh:\n"
        "`cg cook {id món ăn} {số lượng muốn nấu}`\n"
        "Nếu không nhập số lượng thì mặc định là **1**."
    )

    def __init__(
        self,
        authorId: int,
        currentPage: int,
        totalPage: int,
    ):
        super().__init__(timeout=600)

        self.authorId = authorId
        self.currentPage = currentPage
        self.totalPage = totalPage
        self.farmRecipeRenderService = FarmRecipeRenderService()

        self.updateButtonState()

    def updateButtonState(self):
        self.previousButton.disabled = self.currentPage <= 1
        self.nextButton.disabled = self.currentPage >= self.totalPage

    async def interaction_check(self, interaction: discord.Interaction):
        if interaction.user.id != self.authorId:
            await interaction.response.send_message(
                "Bạn không thể điều khiển bảng công thức của người khác.",
                ephemeral=True,
            )
            return False

        return True

    @discord.ui.button(label="Làm mới", emoji="🔄", style=discord.ButtonStyle.primary)
    async def refreshButton(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.refreshRecipeMessage(interaction)

    @discord.ui.button(label="Trước", emoji="⬅️", style=discord.ButtonStyle.secondary)
    async def previousButton(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.currentPage > 1:
            self.currentPage -= 1

        await self.refreshRecipeMessage(interaction)

    @discord.ui.button(label="Tiếp", emoji="➡️", style=discord.ButtonStyle.secondary)
    async def nextButton(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.currentPage < self.totalPage:
            self.currentPage += 1

        await self.refreshRecipeMessage(interaction)

    async def refreshRecipeMessage(self, interaction: discord.Interaction):
        renderResult = self.farmRecipeRenderService.renderRecipePageToBuffer(
            page=self.currentPage,
        )

        self.currentPage = renderResult["currentPage"]
        self.totalPage = renderResult["totalPage"]

        self.updateButtonState()

        file = discord.File(
            renderResult["buffer"],
            filename="recipes.png",
        )

        await interaction.response.edit_message(
            content=self.COOK_GUIDE_TEXT,
            attachments=[file],
            view=self,
        )