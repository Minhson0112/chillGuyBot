import discord

from bot.enums.paymentType import PaymentType
from bot.helper.numberFormatHelper import formatNumber
from bot.services.serverItem.serverItemPaymentService import ServerItemPaymentService


class OwoLoveShopPaymentChannelService:
    def __init__(self):
        self.serverItemPaymentService = ServerItemPaymentService()

    async def handleLoveShopPayment(
        self,
        message: discord.Message,
        senderMember: discord.Member,
        memberPaymentTransactionId: int,
        cowoncyAmount: int,
    ):
        paymentResult = self.serverItemPaymentService.verifyPayment(
            memberPaymentTransactionId=memberPaymentTransactionId,
            paymentType=PaymentType.COWONCY.value,
            paymentAmount=cowoncyAmount,
        )

        if not paymentResult["success"]:
            await message.channel.send(
                embed=self.buildPaymentFailedEmbed(
                    senderMember=senderMember,
                    paymentResult=paymentResult,
                ),
                allowed_mentions=discord.AllowedMentions.none(),
            )
            return True

        completeResult = self.serverItemPaymentService.completePayment(
            memberPaymentTransactionId=paymentResult["memberPaymentTransactionId"],
            paymentType=PaymentType.COWONCY.value,
            paymentAmount=cowoncyAmount,
        )

        if not completeResult["success"]:
            await message.channel.send(
                embed=self.buildPaymentErrorEmbed(
                    title="Cập nhật giao dịch love shop thất bại",
                    description=(
                        f"Người thanh toán: {senderMember.mention}\n"
                        f"Nội dung lỗi: {completeResult['message']}"
                    ),
                ),
                allowed_mentions=discord.AllowedMentions.none(),
            )
            return True

        await message.channel.send(
            embed=self.buildPaymentCompletedEmbed(
                senderMember=senderMember,
                itemName=completeResult["itemName"],
                itemEmoji=completeResult["itemEmoji"],
                quantity=completeResult["quantity"],
                cowoncyAmount=cowoncyAmount,
            ),
            allowed_mentions=discord.AllowedMentions.none(),
        )

        return True

    def buildPaymentFailedEmbed(
        self,
        senderMember: discord.Member,
        paymentResult: dict,
    ):
        embed = discord.Embed(
            title="Thanh toán love shop chưa hoàn tất",
            description=(
                f"Người thanh toán: {senderMember.mention}\n"
                f"Nội dung: {paymentResult['message']}"
            ),
            color=discord.Color.orange(),
        )

        itemName = paymentResult.get("itemName")

        if itemName is not None:
            embed.add_field(
                name="Item đang chờ thanh toán",
                value=self.buildItemText(
                    itemName=itemName,
                    itemEmoji=paymentResult.get("itemEmoji"),
                    quantity=paymentResult.get("quantity"),
                ),
                inline=False,
            )

        return embed

    def buildPaymentCompletedEmbed(
        self,
        senderMember: discord.Member,
        itemName: str,
        itemEmoji: str | None,
        quantity: int,
        cowoncyAmount: int,
    ):
        embed = discord.Embed(
            title="Thanh toán love shop thành công",
            description=(
                f"Người mua: {senderMember.mention}\n"
                f"Item đã mua: {self.buildItemText(itemName, itemEmoji, quantity)}\n"
                f"Số tiền: **{formatNumber(cowoncyAmount)}** <:OwO:1503021935724859473> owo\n"
                "Xem kho của bạn bằng lệnh `cg inv`"
            ),
            color=discord.Color.green(),
        )

        return embed

    def buildPaymentErrorEmbed(
        self,
        title: str,
        description: str,
    ):
        embed = discord.Embed(
            title=title,
            description=description,
            color=discord.Color.red(),
        )

        return embed

    def buildItemText(self, itemName: str, itemEmoji: str | None, quantity: int | None):
        itemText = f"**{itemName}**" if itemEmoji is None else f"{itemEmoji} **{itemName}**"

        if quantity is None:
            return itemText

        return f"{itemText} x**{formatNumber(quantity)}**"
