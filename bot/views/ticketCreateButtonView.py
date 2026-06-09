import discord

from bot.config.emoji import TICK
from bot.views.ticketTypeSelectView import TicketTypeSelectView


TICKET_CREATE_BUTTON_CUSTOM_ID = "ticket_create_button"


class TicketCreateButtonView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="Tạo Ticket",
        style=discord.ButtonStyle.primary,
        emoji=TICK,
        custom_id=TICKET_CREATE_BUTTON_CUSTOM_ID,
    )
    async def createTicketButton(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button,
    ):
        await interaction.response.send_message(
            "Bạn muốn tạo ticket về vấn đề nào?",
            view=TicketTypeSelectView(interaction.user.id),
            ephemeral=True,
        )
