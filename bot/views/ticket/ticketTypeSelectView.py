import discord

from bot.enums.ticketType import TicketType
from bot.services.ticket.ticketChannelService import TicketChannelService


class TicketTypeSelect(discord.ui.Select):
    def __init__(self):
        options = []

        for ticketType in TicketType:
            options.append(
                discord.SelectOption(
                    label=ticketType.label,
                    value=ticketType.value,
                    description=ticketType.description,
                    emoji=ticketType.emoji,
                )
            )

        super().__init__(
            placeholder="Chọn loại ticket",
            min_values=1,
            max_values=1,
            options=options,
        )

    async def callback(self, interaction: discord.Interaction):
        view = self.view
        selectedTicketType = TicketType(self.values[0])

        if not isinstance(view, TicketTypeSelectView):
            await interaction.response.send_message(
                "Không thể xác định dropdown ticket.",
                ephemeral=True,
            )
            return

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

        await interaction.response.defer(ephemeral=True)

        try:
            ticketChannel = await view.ticketChannelService.createTicketChannel(
                guild=interaction.guild,
                member=member,
                ticketType=selectedTicketType,
            )
        except discord.Forbidden:
            await interaction.edit_original_response(
                content="Bot không có quyền tạo kênh ticket.",
                view=None,
            )
            return
        except discord.HTTPException:
            await interaction.edit_original_response(
                content="Đã xảy ra lỗi khi tạo kênh ticket. Vui lòng thử lại sau.",
                view=None,
            )
            return

        await interaction.edit_original_response(
            content=f"Đã tạo ticket tại {ticketChannel.mention}.",
            view=None,
        )


class TicketTypeSelectView(discord.ui.View):
    def __init__(self, authorId: int):
        super().__init__(timeout=180)

        self.authorId = authorId
        self.ticketChannelService = TicketChannelService()
        self.add_item(TicketTypeSelect())

    async def interaction_check(self, interaction: discord.Interaction):
        if interaction.user.id != self.authorId:
            await interaction.response.send_message(
                "Bạn không thể chọn loại ticket thay cho người khác.",
                ephemeral=True,
            )
            return False

        return True
