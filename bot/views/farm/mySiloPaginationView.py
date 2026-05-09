import discord

from bot.services.farm.farmInventoryRenderService import FarmInventoryRenderService


class MySiloPaginationView(discord.ui.View):
    GUIDE_TEXT = (
        "Để bán đồ hãy dùng lệnh:\n"
        "`cg sell {id món đồ} {số lượng muốn bán}`\n"
        "Nếu không nhập số lượng thì mặc định là **1**."
    )
    def __init__(
        self,
        authorId: int,
        memberDisplayName: str,
        currentPage: int,
        totalPage: int,
    ):
        super().__init__(timeout=180)

        self.authorId = authorId
        self.memberDisplayName = memberDisplayName
        self.currentPage = currentPage
        self.totalPage = totalPage
        self.farmInventoryRenderService = FarmInventoryRenderService()

        self.updateButtonState()

    def updateButtonState(self):
        self.previousButton.disabled = self.currentPage <= 1
        self.nextButton.disabled = self.currentPage >= self.totalPage

    async def updateSiloMessage(self, interaction: discord.Interaction):
        renderResult = self.farmInventoryRenderService.renderSiloPageToBuffer(
            userId=self.authorId,
            memberDisplayName=self.memberDisplayName,
            page=self.currentPage,
        )

        self.currentPage = renderResult["currentPage"]
        self.totalPage = renderResult["totalPage"]

        self.updateButtonState()

        file = discord.File(
            renderResult["buffer"],
            filename="my_silo.png",
        )

        await interaction.response.edit_message(
            content=self.GUIDE_TEXT,
            attachments=[file],
            view=self,
        )

    async def interaction_check(self, interaction: discord.Interaction):
        if interaction.user.id != self.authorId:
            await interaction.response.send_message(
                "Bạn không thể điều khiển silo của người khác.",
                ephemeral=True,
            )
            return False

        return True

    @discord.ui.button(label="Làm mới", emoji="🔄", style=discord.ButtonStyle.primary)
    async def refreshButton(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.updateSiloMessage(interaction)

    @discord.ui.button(label="Trước", emoji="⬅️", style=discord.ButtonStyle.secondary)
    async def previousButton(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.currentPage > 1:
            self.currentPage -= 1

        await self.updateSiloMessage(interaction)

    @discord.ui.button(label="Tiếp", emoji="➡️", style=discord.ButtonStyle.secondary)
    async def nextButton(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.currentPage < self.totalPage:
            self.currentPage += 1

        await self.updateSiloMessage(interaction)