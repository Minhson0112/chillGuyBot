import discord

from bot.helper.discordResolverHelper import resolveGuildMember
from bot.config.emoji import LOGO
from bot.config.userId import OWNER_ID, TREASURER_MEMBER_ID_LIST
from bot.enums.memberPaymentTargetType import MemberPaymentTargetType
from bot.services.donate.donateRewardService import DonateRewardService
from bot.services.exchange.owoExchangeCoinService import OwoExchangeCoinService
from bot.services.memberPayment.memberPaymentService import MemberPaymentService
from bot.services.owo.owoLottoTicketPaymentChannelService import OwoLottoTicketPaymentChannelService
from bot.services.owo.owoRoleShopPaymentChannelService import OwoRoleShopPaymentChannelService


class OwoGiveChannelService:
    def __init__(self):
        self.donateRewardService = DonateRewardService()
        self.owoExchangeCoinService = OwoExchangeCoinService()
        self.memberPaymentService = MemberPaymentService()
        self.lottoTicketPaymentChannelService = OwoLottoTicketPaymentChannelService()
        self.roleShopPaymentChannelService = OwoRoleShopPaymentChannelService()

    async def handleDonateChannel(
        self,
        message: discord.Message,
        senderUserId: int,
        receiverUserId: int,
        cowoncyAmount: int,
    ):
        if receiverUserId not in TREASURER_MEMBER_ID_LIST:
            return False

        senderMember = await resolveGuildMember(
            guild=message.guild,
            userId=senderUserId,
        )

        if senderMember is None:
            return False

        receiverMember = await resolveGuildMember(
            guild=message.guild,
            userId=receiverUserId,
        )

        if receiverMember is None:
            return False

        await self.donateRewardService.processDonateReward(
            guild=message.guild,
            senderMember=senderMember,
            receiverMember=receiverMember,
            cowoncyAmount=cowoncyAmount,
        )

        await message.channel.send(
            self.buildThankYouMessage(
                senderMember=senderMember,
                donatedCowoncy=cowoncyAmount,
            )
        )

        return True

    async def handleExchangeCoinChannel(
        self,
        message: discord.Message,
        senderUserId: int,
        receiverUserId: int,
        cowoncyAmount: int,
    ):
        if receiverUserId != OWNER_ID:
            return False

        senderMember = await resolveGuildMember(
            guild=message.guild,
            userId=senderUserId,
        )

        if senderMember is None:
            return False

        receiverMember = await resolveGuildMember(
            guild=message.guild,
            userId=receiverUserId,
        )

        if receiverMember is None:
            return False

        exchangeResult = self.owoExchangeCoinService.exchangeCoin(
            messageId=message.id,
            channelId=message.channel.id,
            senderUserId=senderUserId,
            receiverUserId=receiverUserId,
            cowoncyAmount=cowoncyAmount,
        )

        if not exchangeResult["success"]:
            await message.channel.send(exchangeResult["message"])
            return False

        await message.channel.send(
            self.buildExchangeCoinMessage(
                senderMember=senderMember,
                cowoncyAmount=cowoncyAmount,
                chillCoinAmount=exchangeResult["chillCoinAmount"],
            )
        )

        return True

    async def handlePaymentChannel(
        self,
        message: discord.Message,
        senderUserId: int,
        receiverUserId: int,
        cowoncyAmount: int,
    ):
        if receiverUserId != OWNER_ID and receiverUserId not in TREASURER_MEMBER_ID_LIST:
            return False

        senderMember = await resolveGuildMember(
            guild=message.guild,
            userId=senderUserId,
        )

        if senderMember is None:
            return False

        pendingPaymentResult = self.memberPaymentService.findPendingPaymentByUserId(senderUserId)

        if not pendingPaymentResult["success"]:
            await message.channel.send(
                embed=self.buildPaymentFailedEmbed(
                    senderMember=senderMember,
                    paymentResult=pendingPaymentResult,
                ),
                allowed_mentions=discord.AllowedMentions.none(),
            )
            return True

        paymentTargetType = pendingPaymentResult["paymentTargetType"]

        if paymentTargetType == MemberPaymentTargetType.ROLE_SHOP.value:
            return await self.roleShopPaymentChannelService.handleRoleShopPayment(
                message=message,
                senderMember=senderMember,
                memberPaymentTransactionId=pendingPaymentResult["memberPaymentTransactionId"],
                cowoncyAmount=cowoncyAmount,
            )

        if paymentTargetType == MemberPaymentTargetType.LOTTO_TICKET.value:
            return await self.lottoTicketPaymentChannelService.handleLottoTicketPayment(
                message=message,
                senderMember=senderMember,
                memberPaymentTransactionId=pendingPaymentResult["memberPaymentTransactionId"],
                cowoncyAmount=cowoncyAmount,
            )

        await message.channel.send(
            embed=self.buildPaymentErrorEmbed(
                title="Thanh toán chưa được hỗ trợ",
                description=(
                    f"Người thanh toán: {senderMember.mention}\n"
                    f"Loại giao dịch: `{paymentTargetType}`\n"
                    "Bot chưa hỗ trợ xử lý loại giao dịch này."
                ),
            ),
            allowed_mentions=discord.AllowedMentions.none(),
        )

        return True

    def buildThankYouMessage(
        self,
        senderMember: discord.Member,
        donatedCowoncy: int,
    ):
        return (
            "# <a:CS_decorate:1366286592758779995> Cảm Ơn Donate <a:CS_decorate:1366286658260963450>\n"
            f"Thay mặt {LOGO} cảm ơn {senderMember.mention} rất nhiều <a:CS_tim1:1466240640089325588>, "
            f"chúng tớ đã nhận được {donatedCowoncy:,} cowoncy, chúc bạn một ngày tốt lành.\n"
            "Đừng quên xem qua đặc quyền dành cho donator tại "
            "https://discord.com/channels/1356994231918530690/1502996579366338620/1516263538962862090 nhé."
        )

    def buildExchangeCoinMessage(
        self,
        senderMember: discord.Member,
        cowoncyAmount: int,
        chillCoinAmount: int,
    ):
        return (
            f"{senderMember.mention} đã chuyển **{cowoncyAmount:,}** cowoncy thành công.\n"
            f"Bạn nhận được **{chillCoinAmount:,}** <:cs_coin:1495116560191324383>."
        )

    def buildPaymentFailedEmbed(
        self,
        senderMember: discord.Member,
        paymentResult: dict,
    ):
        embed = discord.Embed(
            title="Thanh toán chưa hoàn tất",
            description=(
                f"Người thanh toán: {senderMember.mention}\n"
                f"Nội dung: {paymentResult['message']}"
            ),
            color=discord.Color.orange(),
        )

        roleId = paymentResult.get("roleId")

        if roleId is not None:
            role = senderMember.guild.get_role(roleId)

            if role is not None:
                embed.add_field(
                    name="Role đang chờ thanh toán",
                    value=role.mention,
                    inline=False,
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
