import traceback

import discord

from bot.config.emoji import JOIN_BUTTON
from bot.services.giveaway.giveawayMessageService import GiveawayMessageService


GIVEAWAY_JOIN_BUTTON_CUSTOM_ID_PREFIX = "giveaway_join"


class GiveawayJoinButtonView(discord.ui.View):
    def __init__(self, giveawayId: int):
        super().__init__(timeout=None)
        self.giveawayId = giveawayId
        self.add_item(GiveawayJoinButton(giveawayId))

    async def on_error(self, interaction: discord.Interaction, error: Exception, item):
        traceback.print_exception(type(error), error, error.__traceback__)

        if interaction.response.is_done():
            await interaction.followup.send(
                "Đã xảy ra lỗi khi tham gia giveaway.",
                ephemeral=True,
            )
            return

        await interaction.response.send_message(
            "Đã xảy ra lỗi khi tham gia giveaway.",
            ephemeral=True,
        )


class GiveawayJoinButton(discord.ui.Button):
    def __init__(self, giveawayId: int):
        super().__init__(
            label="Tham gia",
            style=discord.ButtonStyle.primary,
            emoji=JOIN_BUTTON,
            custom_id=f"{GIVEAWAY_JOIN_BUTTON_CUSTOM_ID_PREFIX}:{giveawayId}",
        )
        self.giveawayId = giveawayId
        self.giveawayMessageService = GiveawayMessageService()

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        if interaction.guild is None:
            await interaction.followup.send(
                "Bạn chỉ có thể tham gia giveaway trong server.",
                ephemeral=True,
            )
            return

        result = self.giveawayMessageService.joinGiveaway(
            giveawayId=self.giveawayId,
            userId=interaction.user.id,
        )

        if not result["success"]:
            await interaction.followup.send(
                result["message"],
                ephemeral=True,
            )
            return

        embed = self.giveawayMessageService.buildGiveawayEmbedById(
            giveawayId=self.giveawayId,
            guild=interaction.guild,
        )

        if embed is not None and interaction.message is not None:
            await interaction.message.edit(
                embed=embed,
                view=GiveawayJoinButtonView(self.giveawayId),
            )

        await interaction.followup.send(
            result["message"],
            ephemeral=True,
        )
