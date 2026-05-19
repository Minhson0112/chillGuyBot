import discord

from bot.config.emoji import FARM_GAME_EMOJI
from bot.services.farm.farmPlantService import FarmPlantService


class PlantSeedSelect(discord.ui.Select):
    def __init__(self, seedOptions):
        options = []

        for seedOption in seedOptions:
            itemEmoji = FARM_GAME_EMOJI.get(seedOption["iconImageKey"])

            options.append(
                discord.SelectOption(
                    label=seedOption["itemName"][:100],
                    value=str(seedOption["userInventoryId"]),
                    description=(
                        f"SL: {seedOption['quantity']} "
                        f"⏱️{seedOption['growthTimeText']}"
                    )[:100],
                    emoji=itemEmoji,
                )
            )

        super().__init__(
            placeholder="Chọn hạt giống muốn trồng",
            min_values=1,
            max_values=1,
            options=options,
        )

    async def callback(self, interaction: discord.Interaction):
        view = self.view
        userInventoryId = int(self.values[0])

        result = view.farmPlantService.plantCrop(
            userId=view.authorId,
            userInventoryId=userInventoryId,
        )

        await interaction.response.edit_message(
            content=result["message"],
            view=None,
        )


class PlantSeedSelectView(discord.ui.View):
    def __init__(
        self,
        authorId: int,
        seedOptions,
    ):
        super().__init__(timeout=180)

        self.authorId = authorId
        self.farmPlantService = FarmPlantService()

        self.add_item(PlantSeedSelect(seedOptions))

    async def interaction_check(self, interaction: discord.Interaction):
        if interaction.user.id != self.authorId:
            await interaction.response.send_message(
                "Bạn không thể trồng cây trên farm của người khác.",
                ephemeral=True,
            )
            return False

        return True