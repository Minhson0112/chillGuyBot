import discord

from bot.services.farm.farmMarketShopRenderService import FarmMarketShopRenderService


class MyFarmShopPaginationView(discord.ui.View):
    def __init__(
        self,
        sellerUserId: int,
        sellerDisplayName: str,
        currentPage: int,
        totalPage: int,
    ):
        super().__init__(timeout=600)

        self.sellerUserId = sellerUserId
        self.sellerDisplayName = sellerDisplayName
        self.currentPage = currentPage
        self.totalPage = totalPage
        self.farmMarketShopRenderService = FarmMarketShopRenderService()

        self.updateButtonState()

    def updateButtonState(self):
        self.previousButton.disabled = self.currentPage <= 1
        self.nextButton.disabled = self.currentPage >= self.totalPage

    @discord.ui.button(label="Trước", emoji="⬅️", style=discord.ButtonStyle.secondary)
    async def previousButton(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.currentPage > 1:
            self.currentPage -= 1

        await self.refreshShopMessage(interaction)

    @discord.ui.button(label="Tiếp", emoji="➡️", style=discord.ButtonStyle.secondary)
    async def nextButton(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.currentPage < self.totalPage:
            self.currentPage += 1

        await self.refreshShopMessage(interaction)

    async def refreshShopMessage(self, interaction: discord.Interaction):
        renderResult = self.farmMarketShopRenderService.renderMemberShopPageToBuffer(
            sellerUserId=self.sellerUserId,
            memberDisplayName=self.sellerDisplayName,
            page=self.currentPage,
        )

        self.currentPage = renderResult["currentPage"]
        self.totalPage = renderResult["totalPage"]

        self.updateButtonState()

        file = discord.File(
            renderResult["buffer"],
            filename="my_shop.png",
        )

        embed = self.buildShopEmbed()
        embed.set_image(url="attachment://my_shop.png")

        await interaction.response.edit_message(
            embed=embed,
            attachments=[file],
            view=self,
        )

    def buildShopEmbed(self):
        return discord.Embed(
            title=f"Shop của {self.sellerDisplayName}",
            description=(
                "Dùng `cg buyshop <id>` để mua món hàng trong shop này.\n"
                f"Trang **{self.currentPage} / {self.totalPage}**"
            ),
            color=discord.Color.gold(),
        )