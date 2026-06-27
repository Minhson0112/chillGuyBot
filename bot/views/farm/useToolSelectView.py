import discord

from bot.config.emoji import FARM_GAME_EMOJI
from bot.enums.toolStatus import ToolStatus
from bot.services.farm.farmToolUseService import FarmToolUseService


class UseToolSelect(discord.ui.Select):
    def __init__(self, toolOptions):
        options = []

        for toolOption in toolOptions:
            itemEmoji = FARM_GAME_EMOJI.get(toolOption["iconImageKey"])

            options.append(
                discord.SelectOption(
                    label=f"{toolOption['itemName']} #{toolOption['userToolId']}"[:100],
                    value=str(toolOption["userToolId"]),
                    description=self.buildDescription(toolOption)[:100],
                    emoji=itemEmoji,
                )
            )

        super().__init__(
            placeholder="Chọn công cụ muốn lắp vào farm",
            min_values=1,
            max_values=1,
            options=options,
        )

    def buildDescription(self, toolOption):
        description = f"Độ bền: {toolOption['durabilityText']}"

        if toolOption["status"] == ToolStatus.EQUIPPED.value:
            description += " • In use"

        return description

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()

        view = self.view
        userToolId = int(self.values[0])

        result = view.farmToolUseService.useTool(
            userId=view.authorId,
            userToolId=userToolId,
        )

        await interaction.edit_original_response(
            content=result["message"],
            view=None,
        )


class UseToolSelectView(discord.ui.View):
    def __init__(
        self,
        authorId: int,
        toolOptions,
    ):
        super().__init__(timeout=180)

        self.authorId = authorId
        self.farmToolUseService = FarmToolUseService()

        self.add_item(UseToolSelect(toolOptions))

    async def interaction_check(self, interaction: discord.Interaction):
        if interaction.user.id != self.authorId:
            await interaction.response.send_message(
                "Bạn không thể lắp công cụ vào farm của người khác.",
                ephemeral=True,
            )
            return False

        return True
