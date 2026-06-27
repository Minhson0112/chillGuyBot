import discord

from bot.services.farm.farmInventoryRenderService import FarmInventoryRenderService


class MyToolBagPaginationView(discord.ui.View):
    GUIDE_TEXT = (
        "Dùng `cg use {id công cụ} để sử dụng trong farm`.\n"
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

    async def updateToolBagMessage(self, interaction: discord.Interaction):
        await interaction.response.defer()

        renderResult = self.farmInventoryRenderService.renderToolBagPageToBuffer(
            userId=self.authorId,
            memberDisplayName=self.memberDisplayName,
            page=self.currentPage,
        )

        self.currentPage = renderResult["currentPage"]
        self.totalPage = renderResult["totalPage"]

        self.updateButtonState()

        file = discord.File(
            renderResult["buffer"],
            filename="my_toolbag.png",
        )

        await interaction.edit_original_response(
            content=self.GUIDE_TEXT,
            attachments=[file],
            view=self,
        )

    async def interaction_check(self, interaction: discord.Interaction):
        if interaction.user.id != self.authorId:
            await interaction.response.send_message(
                "Bạn không thể điều khiển túi dụng cụ của người khác.",
                ephemeral=True,
            )
            return False

        return True

    @discord.ui.button(label="Hướng dẫn", emoji="📖", style=discord.ButtonStyle.primary)
    async def refreshButton(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.updateToolBagMessage(interaction)

    @discord.ui.button(label="Trước", emoji="⬅️", style=discord.ButtonStyle.secondary)
    async def previousButton(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.currentPage > 1:
            self.currentPage -= 1

        await self.updateToolBagMessage(interaction)

    @discord.ui.button(label="Tiếp", emoji="➡️", style=discord.ButtonStyle.secondary)
    async def nextButton(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.currentPage < self.totalPage:
            self.currentPage += 1

        await self.updateToolBagMessage(interaction)
