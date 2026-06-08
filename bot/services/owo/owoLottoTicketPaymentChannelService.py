import discord

from bot.enums.paymentType import PaymentType
from bot.services.lotto.lottoTicketPaymentService import LottoTicketPaymentService
from bot.services.lotto.lottoTicketMessageService import LottoTicketMessageService


class OwoLottoTicketPaymentChannelService:
    def __init__(self):
        self.lottoTicketPaymentService = LottoTicketPaymentService()
        self.lottoTicketMessageService = LottoTicketMessageService()

    async def handleLottoTicketPayment(
        self,
        message: discord.Message,
        senderMember: discord.Member,
        memberPaymentTransactionId: int,
        cowoncyAmount: int,
    ):
        paymentResult = self.lottoTicketPaymentService.completePayment(
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

        await message.channel.send(
            embed=self.lottoTicketMessageService.buildLottoPaymentCompletedEmbed(
                member=senderMember,
                tickets=paymentResult["tickets"],
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
            title="Thanh toán vé lotto chưa hoàn tất",
            description=(
                f"Người thanh toán: {senderMember.mention}\n"
                f"Nội dung: {paymentResult['message']}"
            ),
            color=discord.Color.orange(),
        )

        return embed
