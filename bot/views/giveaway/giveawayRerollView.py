import traceback

import discord

from bot.services.giveaway.giveawayDrawService import GiveawayDrawService


GIVEAWAY_REROLL_BUTTON_CUSTOM_ID_PREFIX = "giveaway_reroll"
GIVEAWAY_REROLL_SELECT_CUSTOM_ID_PREFIX = "giveaway_reroll_select"
DISCORD_SELECT_MAX_OPTIONS = 25


class GiveawayRerollView(discord.ui.View):
    def __init__(
        self,
        giveawayId: int,
        winners,
    ):
        super().__init__(timeout=None)
        self.giveawayId = giveawayId
        self.winners = winners

        if len(winners) == 1:
            self.add_item(GiveawayRerollButton(giveawayId, winners[0].id))
            return

        if len(winners) > 1:
            self.add_item(GiveawayRerollSelect(giveawayId, winners))

    async def on_error(self, interaction: discord.Interaction, error: Exception, item):
        traceback.print_exception(type(error), error, error.__traceback__)

        if interaction.response.is_done():
            await interaction.followup.send(
                "Đã xảy ra lỗi khi reroll giveaway.",
                ephemeral=True,
            )
            return

        await interaction.response.send_message(
            "Đã xảy ra lỗi khi reroll giveaway.",
            ephemeral=True,
        )


class GiveawayRerollButton(discord.ui.Button):
    def __init__(
        self,
        giveawayId: int,
        winnerId: int,
    ):
        super().__init__(
            label="Reroll",
            style=discord.ButtonStyle.danger,
            custom_id=f"{GIVEAWAY_REROLL_BUTTON_CUSTOM_ID_PREFIX}:{giveawayId}:{winnerId}",
        )
        self.giveawayId = giveawayId
        self.winnerId = winnerId
        self.giveawayDrawService = GiveawayDrawService()

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        result = self.giveawayDrawService.rerollWinner(
            giveawayId=self.giveawayId,
            winnerId=self.winnerId,
            requestedByUserId=interaction.user.id,
        )

        await sendRerollResult(
            interaction=interaction,
            result=result,
            giveawayId=self.giveawayId,
        )


class GiveawayRerollSelect(discord.ui.Select):
    def __init__(
        self,
        giveawayId: int,
        winners,
    ):
        options = [
            discord.SelectOption(
                label=f"Slot {winner.current_slot_number} - {winner.user_id}",
                value=str(winner.id),
                description=f"Reroll <@{winner.user_id}>",
            )
            for winner in winners[:DISCORD_SELECT_MAX_OPTIONS]
        ]

        super().__init__(
            custom_id=f"{GIVEAWAY_REROLL_SELECT_CUSTOM_ID_PREFIX}:{giveawayId}",
            placeholder="Chọn người thắng cần reroll",
            min_values=1,
            max_values=1,
            options=options,
        )
        self.giveawayId = giveawayId
        self.giveawayDrawService = GiveawayDrawService()

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        result = self.giveawayDrawService.rerollWinner(
            giveawayId=self.giveawayId,
            winnerId=int(self.values[0]),
            requestedByUserId=interaction.user.id,
        )

        await sendRerollResult(
            interaction=interaction,
            result=result,
            giveawayId=self.giveawayId,
        )


async def sendRerollResult(
    interaction: discord.Interaction,
    result: dict,
    giveawayId: int,
):
    if not result["success"]:
        await interaction.followup.send(
            result["message"],
            ephemeral=True,
        )
        return

    if interaction.message is None:
        await interaction.followup.send(
            "Không thể xác định tin nhắn reroll.",
            ephemeral=True,
        )
        return

    await interaction.message.reply(
        content=result["message"],
        view=GiveawayRerollView(
            giveawayId=giveawayId,
            winners=result["winners"],
        ),
        allowed_mentions=discord.AllowedMentions(
            users=True,
            roles=False,
            everyone=False,
        ),
    )

    await interaction.followup.send(
        "Đã reroll giveaway.",
        ephemeral=True,
    )
