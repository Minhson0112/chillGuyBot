import discord

from bot.config.emoji import FARM_GAME_EMOJI
from bot.services.farm.farmMarketListingReclaimService import FarmMarketListingReclaimService


class FarmMarketListingReclaimSelect(discord.ui.Select):
    def __init__(self, reclaimOptions):
        options = []

        for reclaimOption in reclaimOptions:
            options.append(
                discord.SelectOption(
                    label=reclaimOption["itemName"][:100],
                    value=str(reclaimOption["listingId"]),
                    description=(
                        f"ID: {reclaimOption['listingId']} | "
                        f"Số lượng: {reclaimOption['quantity']}"
                    )[:100],
                    emoji=FARM_GAME_EMOJI.get(reclaimOption["iconImageKey"]),
                )
            )

        super().__init__(
            placeholder="Chọn món đồ muốn lấy lại",
            min_values=1,
            max_values=1,
            options=options,
        )

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()

        view = self.view
        listingId = int(self.values[0])
        result = view.farmMarketListingReclaimService.reclaimListing(
            userId=view.authorId,
            listingId=listingId,
        )

        await interaction.edit_original_response(
            content=result["message"],
            view=None,
        )

        if result["success"]:
            await view.shopView.refreshShopMessageByInteraction(view.shopInteraction)


class FarmMarketListingReclaimView(discord.ui.View):
    def __init__(
        self,
        authorId: int,
        reclaimOptions,
        shopView,
        shopInteraction,
    ):
        super().__init__(timeout=180)

        self.authorId = authorId
        self.shopView = shopView
        self.shopInteraction = shopInteraction
        self.farmMarketListingReclaimService = FarmMarketListingReclaimService()

        self.add_item(FarmMarketListingReclaimSelect(reclaimOptions))

    async def interaction_check(self, interaction: discord.Interaction):
        if interaction.user.id != self.authorId:
            await interaction.response.send_message(
                "Bạn không thể lấy lại món đồ của shop khác.",
                ephemeral=True,
            )
            return False

        return True
