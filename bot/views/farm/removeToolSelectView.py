import discord

from bot.config.emoji import FARM_GAME_EMOJI
from bot.services.farm.farmToolRemoveService import FarmToolRemoveService


class RemoveToolSelect(discord.ui.Select):
    def __init__(self, toolOptions):
        options = []

        for toolOption in toolOptions:
            itemEmoji = FARM_GAME_EMOJI.get(toolOption["iconImageKey"])

            options.append(
                discord.SelectOption(
                    label=f"{toolOption['itemName']} #{toolOption['userToolId']}"[:100],
                    value=str(toolOption["userToolId"]),
                    description=f"Độ bền: {toolOption['durabilityText']} • In use"[:100],
                    emoji=itemEmoji,
                )
            )

        super().__init__(
            placeholder="Chọn công cụ muốn gỡ khỏi farm",
            min_values=1,
            max_values=1,
            options=options,
        )

    async def callback(self, interaction: discord.Interaction):
        view = self.view
        userToolId = int(self.values[0])

        result = view.farmToolRemoveService.removeTool(
            userId=view.authorId,
            userToolId=userToolId,
        )

        await interaction.response.edit_message(
            content=result["message"],
            view=None,
        )


class RemoveToolSelectView(discord.ui.View):
    def __init__(
        self,
        authorId: int,
        toolOptions,
    ):
        super().__init__(timeout=180)

        self.authorId = authorId
        self.farmToolRemoveService = FarmToolRemoveService()

        self.add_item(RemoveToolSelect(toolOptions))

    async def interaction_check(self, interaction: discord.Interaction):
        if interaction.user.id != self.authorId:
            await interaction.response.send_message(
                "Bạn không thể gỡ công cụ khỏi farm của người khác.",
                ephemeral=True,
            )
            return False

        return True
