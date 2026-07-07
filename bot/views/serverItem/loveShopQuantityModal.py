import traceback

import discord

from bot.config.channel import PAYMENT_CHANNEL_ID
from bot.config.emoji import CHILL_COIN, COWONCCY
from bot.config.userId import OWNER_ID
from bot.helper.numberFormatHelper import formatNumber
from bot.services.serverItem.serverItemPurchaseService import ServerItemPurchaseService


class LoveShopQuantityModal(discord.ui.Modal, title="Mua item love shop"):
    quantity = discord.ui.TextInput(
        label="Số lượng muốn mua",
        placeholder="Ví dụ: 1",
        required=True,
        max_length=5,
    )

    def __init__(self, itemId: int):
        super().__init__()
        self.itemId = itemId
        self.serverItemPurchaseService = ServerItemPurchaseService()

    async def on_submit(self, interaction: discord.Interaction):
        try:
            quantity = int(self.quantity.value.strip())
        except ValueError:
            await interaction.response.send_message(
                "Số lượng item không hợp lệ.",
                ephemeral=True,
            )
            return

        await interaction.response.defer(ephemeral=True)

        try:
            result = self.serverItemPurchaseService.createPendingPurchase(
                userId=interaction.user.id,
                itemId=self.itemId,
                quantity=quantity,
            )

            if not result["success"]:
                await interaction.followup.send(
                    result["message"],
                    ephemeral=True,
                )
                return

            await interaction.followup.send(
                f"Bạn đã đăng kí mua **{formatNumber(result['quantity'])}** x {self.buildItemText(result)} thành công.\n"
                f"Để hoàn tất giao dịch, bạn hãy chuyển phí giao dịch cho <@{OWNER_ID}> ở kênh <#{PAYMENT_CHANNEL_ID}>.\n\n"
                f"Số tiền cần chuyển: {self.buildPaymentText(result)}\n\n"
                "Để hủy giao dịch hãy dùng lệnh `cg cancelloveshop`",
                ephemeral=True,
            )
        except Exception as e:
            print(f"Love shop purchase submit error: {e}")
            traceback.print_exception(type(e), e, e.__traceback__)
            await interaction.followup.send(
                "Đã xảy ra lỗi khi đăng kí mua item love shop. Vui lòng thử lại sau.",
                ephemeral=True,
            )

    def buildPaymentText(self, result: dict):
        prices = []

        if result["priceCowoncy"] is not None and result["priceCowoncy"] > 0:
            prices.append(f"**{formatNumber(result['priceCowoncy'])}** {COWONCCY} owo")

        if result["priceChillCoin"] is not None and result["priceChillCoin"] > 0:
            prices.append(f"**{formatNumber(result['priceChillCoin'])}** {CHILL_COIN} chill coin")

        return " hoặc ".join(prices)

    def buildItemText(self, result: dict):
        if result["itemEmoji"] is None:
            return f"**{result['itemName']}**"

        return f"{result['itemEmoji']} **{result['itemName']}**"
