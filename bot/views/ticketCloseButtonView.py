import discord

from bot.config.roles import ADMIN_ROLE_ID, MODERATOR_ROLE_ID, OWNER_ROLE_ID


TICKET_CLOSE_BUTTON_CUSTOM_ID = "ticket_close_button"
TICKET_CLOSE_ROLE_IDS = {
    OWNER_ROLE_ID,
    ADMIN_ROLE_ID,
    MODERATOR_ROLE_ID,
}


class TicketCloseButtonView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="Close Ticket",
        style=discord.ButtonStyle.danger,
        custom_id=TICKET_CLOSE_BUTTON_CUSTOM_ID,
    )
    async def closeTicketButton(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button,
    ):
        if interaction.guild is None:
            await interaction.response.send_message(
                "Lệnh này chỉ dùng được trong server.",
                ephemeral=True,
            )
            return

        member = interaction.user

        if not isinstance(member, discord.Member):
            await interaction.response.send_message(
                "Không thể xác định thông tin member của bạn.",
                ephemeral=True,
            )
            return

        if not self.canCloseTicket(member):
            await interaction.response.send_message(
                "Bạn không có quyền đóng ticket này.",
                ephemeral=True,
            )
            return

        channel = interaction.channel

        if not isinstance(channel, discord.TextChannel):
            await interaction.response.send_message(
                "Không thể xoá kênh ticket này.",
                ephemeral=True,
            )
            return

        await interaction.response.defer(ephemeral=True)
        await channel.delete(reason=f"Ticket closed by {member}")

    def canCloseTicket(self, member: discord.Member):
        return any(role.id in TICKET_CLOSE_ROLE_IDS for role in member.roles)
