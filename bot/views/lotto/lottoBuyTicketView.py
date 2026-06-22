import traceback

import discord

from bot.config.channel import PAYMENT_CHANNEL_ID
from bot.config.emoji import COWONCCY
from bot.config.userId import OWNER_ID
from bot.services.lotto.lottoTicketPurchaseService import LottoTicketPurchaseService


class BuyLottoTicketModal(discord.ui.Modal, title="Mua vé lotto"):
    ticketQuantity = discord.ui.TextInput(
        label="Số lượng vé muốn mua",
        placeholder="Ví dụ: 1",
        required=True,
        max_length=5,
    )

    def __init__(self, lottoEventId: int):
        super().__init__()
        self.lottoEventId = lottoEventId
        self.lottoTicketPurchaseService = LottoTicketPurchaseService()

    async def on_submit(self, interaction: discord.Interaction):
        try:
            ticketQuantity = int(str(self.ticketQuantity).strip())
        except ValueError:
            await interaction.response.send_message(
                "Số lượng vé lotto không hợp lệ.",
                ephemeral=True,
            )
            return

        result = self.lottoTicketPurchaseService.createPendingPurchase(
            userId=interaction.user.id,
            lottoEventId=self.lottoEventId,
            ticketQuantity=ticketQuantity,
        )

        if not result["success"]:
            await interaction.response.send_message(
                result["message"],
                ephemeral=True,
            )
            return

        await interaction.response.send_message(
            f"Bạn đã đăng kí mua **{result['ticketQuantity']}** vé lotto cho event **{result['lottoEventName']}**.\n"
            f"Số tiền cần thanh toán: **{result['paymentAmount']:,}** {COWONCCY}.\n"
            f"Hãy give cho <@{OWNER_ID}> tại kênh <#{PAYMENT_CHANNEL_ID}>.\n"
            "Nếu muốn huỷ giao dịch hãy dùng lệnh `cg cancellotto`.",
            ephemeral=True,
        )


class LottoBuyTicketButton(discord.ui.Button):
    def __init__(self, lottoEventId: int):
        super().__init__(
            label="Mua vé lotto",
            style=discord.ButtonStyle.primary,
            custom_id=f"lotto_buy_ticket:{lottoEventId}",
        )
        self.lottoEventId = lottoEventId

    async def callback(self, interaction: discord.Interaction):
        if interaction.guild is None:
            await interaction.response.send_message(
                "Lệnh mua vé lotto chỉ dùng được trong server.",
                ephemeral=True,
            )
            return

        await interaction.response.send_modal(BuyLottoTicketModal(self.lottoEventId))


class LottoBuyTicketView(discord.ui.View):
    def __init__(self, lottoEventId: int):
        super().__init__(timeout=None)
        self.add_item(LottoBuyTicketButton(lottoEventId))

    async def on_error(self, interaction: discord.Interaction, error: Exception, item):
        traceback.print_exception(type(error), error, error.__traceback__)

        if interaction.response.is_done():
            await interaction.followup.send(
                "Đã xảy ra lỗi khi xử lý nút mua vé lotto.",
                ephemeral=True,
            )
            return

        await interaction.response.send_message(
            "Đã xảy ra lỗi khi xử lý nút mua vé lotto.",
            ephemeral=True,
        )
