import discord

from bot.services.farm.farmItemSellService import FarmItemSellService


class SellFarmItemView(discord.ui.View):
    def __init__(
        self,
        authorId: int,
        inventoryId: int,
        quantity: int,
    ):
        super().__init__(timeout=60)

        self.authorId = authorId
        self.inventoryId = inventoryId
        self.quantity = quantity
        self.isFinished = False
        self.message = None
        self.farmItemSellService = FarmItemSellService()

    async def interaction_check(self, interaction: discord.Interaction):
        if interaction.user.id != self.authorId:
            await interaction.response.send_message(
                "Bạn không thể xác nhận bán item của người khác.",
                ephemeral=True,
            )
            return False

        return True

    @discord.ui.button(label="Xác nhận", style=discord.ButtonStyle.success)
    async def confirmButton(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button,
    ):
        if self.isFinished:
            await interaction.response.send_message(
                "Yêu cầu bán item này đã được xử lý.",
                ephemeral=True,
            )
            return

        self.isFinished = True
        self.disableButtons()
        await interaction.response.defer()

        try:
            sellResult = self.farmItemSellService.sellItem(
                userId=interaction.user.id,
                inventoryId=self.inventoryId,
                quantity=self.quantity,
            )

            await interaction.edit_original_response(
                content=sellResult["message"],
                embed=None,
                view=self,
                allowed_mentions=discord.AllowedMentions.none(),
            )

        except Exception as e:
            print(f"Sell farm item confirm error: {e}")
            await interaction.edit_original_response(
                content="Đã xảy ra lỗi khi bán item.",
                embed=None,
                view=self,
            )

        self.stop()

    @discord.ui.button(label="Hủy", style=discord.ButtonStyle.danger)
    async def cancelButton(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button,
    ):
        if self.isFinished:
            await interaction.response.send_message(
                "Yêu cầu bán item này đã được xử lý.",
                ephemeral=True,
            )
            return

        self.isFinished = True
        self.disableButtons()

        await interaction.response.edit_message(
            content="Đã hủy bán item.",
            embed=None,
            view=self,
            allowed_mentions=discord.AllowedMentions.none(),
        )
        self.stop()

    async def on_timeout(self):
        if self.isFinished:
            return

        self.isFinished = True
        self.disableButtons()

        if self.message is not None:
            await self.message.edit(view=self)

    def disableButtons(self):
        for child in self.children:
            child.disabled = True
