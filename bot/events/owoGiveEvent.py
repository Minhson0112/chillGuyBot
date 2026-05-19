import re

import discord
from discord.ext import commands

from bot.config.channel import DONATE_CHANNEL_ID, EXCHANGE_COIN_CHANNEL_ID, PAYMENT_CHANNEL_ID
from bot.config.emoji import LOGO
from bot.config.userId import OWNER_ID, OWO_BOT_ID, TREASURER_MEMBER_ID_LIST
from bot.enums.paymentType import PaymentType
from bot.services.donate.donateRewardService import DonateRewardService
from bot.services.exchange.owoExchangeCoinService import OwoExchangeCoinService
from bot.services.roleShop.roleShopPaymentService import RoleShopPaymentService


class OwoGiveEvent(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.donateRewardService = DonateRewardService()
        self.owoExchangeCoinService = OwoExchangeCoinService()
        self.roleShopPaymentService = RoleShopPaymentService()
        self.processedMessageIds = set()

    @commands.Cog.listener()
    async def on_message_edit(self, before: discord.Message, after: discord.Message):
        if before.content == after.content:
            return

        await self.handleOwoGiveMessage(after)

    async def handleOwoGiveMessage(self, message: discord.Message):
        if message.guild is None:
            return

        if message.author.id != OWO_BOT_ID:
            return

        if message.channel.id not in [
            DONATE_CHANNEL_ID,
            EXCHANGE_COIN_CHANNEL_ID,
            PAYMENT_CHANNEL_ID,
        ]:
            return

        if message.id in self.processedMessageIds:
            return

        giveInfo = self.extractOwoGiveInfo(message.content)

        if giveInfo is None:
            return

        senderUserId = giveInfo["senderUserId"]
        receiverUserId = giveInfo["receiverUserId"]
        cowoncyAmount = giveInfo["cowoncyAmount"]

        if message.channel.id == DONATE_CHANNEL_ID:
            await self.handleDonateChannel(
                message=message,
                senderUserId=senderUserId,
                receiverUserId=receiverUserId,
                cowoncyAmount=cowoncyAmount,
            )
            return

        if message.channel.id == EXCHANGE_COIN_CHANNEL_ID:
            await self.handleExchangeCoinChannel(
                message=message,
                senderUserId=senderUserId,
                receiverUserId=receiverUserId,
                cowoncyAmount=cowoncyAmount,
            )
            return

        if message.channel.id == PAYMENT_CHANNEL_ID:
            await self.handlePaymentChannel(
                message=message,
                senderUserId=senderUserId,
                receiverUserId=receiverUserId,
                cowoncyAmount=cowoncyAmount,
            )
            return

    async def handleDonateChannel(
        self,
        message: discord.Message,
        senderUserId: int,
        receiverUserId: int,
        cowoncyAmount: int,
    ):
        if receiverUserId not in TREASURER_MEMBER_ID_LIST:
            return

        senderMember = await self.resolveGuildMember(
            guild=message.guild,
            userId=senderUserId,
        )

        if senderMember is None:
            return

        receiverMember = await self.resolveGuildMember(
            guild=message.guild,
            userId=receiverUserId,
        )

        if receiverMember is None:
            return

        await self.donateRewardService.processDonateReward(
            guild=message.guild,
            senderMember=senderMember,
            receiverMember=receiverMember,
            cowoncyAmount=cowoncyAmount,
        )

        self.processedMessageIds.add(message.id)

        await message.channel.send(
            self.buildThankYouMessage(
                senderMember=senderMember,
                donatedCowoncy=cowoncyAmount,
            )
        )

    async def handleExchangeCoinChannel(
        self,
        message: discord.Message,
        senderUserId: int,
        receiverUserId: int,
        cowoncyAmount: int,
    ):
        if receiverUserId != OWNER_ID:
            return

        senderMember = await self.resolveGuildMember(
            guild=message.guild,
            userId=senderUserId,
        )

        if senderMember is None:
            return

        receiverMember = await self.resolveGuildMember(
            guild=message.guild,
            userId=receiverUserId,
        )

        if receiverMember is None:
            return

        exchangeResult = self.owoExchangeCoinService.exchangeCoin(
            messageId=message.id,
            channelId=message.channel.id,
            senderUserId=senderUserId,
            receiverUserId=receiverUserId,
            cowoncyAmount=cowoncyAmount,
        )

        if not exchangeResult["success"]:
            await message.channel.send(exchangeResult["message"])
            return

        self.processedMessageIds.add(message.id)

        await message.channel.send(
            self.buildExchangeCoinMessage(
                senderMember=senderMember,
                cowoncyAmount=cowoncyAmount,
                chillCoinAmount=exchangeResult["chillCoinAmount"],
            )
        )

    async def handlePaymentChannel(
        self,
        message: discord.Message,
        senderUserId: int,
        receiverUserId: int,
        cowoncyAmount: int,
    ):
        if receiverUserId != OWNER_ID and receiverUserId not in TREASURER_MEMBER_ID_LIST:
            return

        senderMember = await self.resolveGuildMember(
            guild=message.guild,
            userId=senderUserId,
        )

        if senderMember is None:
            return

        paymentResult = self.roleShopPaymentService.verifyPayment(
            userId=senderUserId,
            paymentType=PaymentType.COWONCY.value,
            paymentAmount=cowoncyAmount,
        )

        if not paymentResult["success"]:
            self.processedMessageIds.add(message.id)

            await message.channel.send(
                embed=self.buildRolePaymentFailedEmbed(
                    senderMember=senderMember,
                    paymentResult=paymentResult,
                ),
                allowed_mentions=discord.AllowedMentions.none(),
            )
            return

        role = message.guild.get_role(paymentResult["roleId"])

        if role is None:
            self.processedMessageIds.add(message.id)

            await message.channel.send(
                embed=self.buildRolePaymentErrorEmbed(
                    title="Thanh toán role cần xử lý thủ công",
                    description=(
                        f"Người thanh toán: {senderMember.mention}\n"
                        "User đã thanh toán, nhưng role cần cấp không còn tồn tại trong server.\n"
                        "Vui lòng liên hệ quản trị viên."
                    ),
                ),
                allowed_mentions=discord.AllowedMentions.none(),
            )
            return

        try:
            await senderMember.add_roles(
                role,
                reason="Role shop payment completed",
            )
        except discord.Forbidden:
            self.processedMessageIds.add(message.id)

            await message.channel.send(
                embed=self.buildRolePaymentErrorEmbed(
                    title="Bot không có quyền cấp role",
                    description=(
                        f"Người thanh toán: {senderMember.mention}\n"
                        f"Role cần cấp: {role.mention}\n"
                        "User đã thanh toán, nhưng bot không có quyền cấp role này.\n"
                        "Vui lòng kiểm tra lại vị trí role của bot."
                    ),
                ),
                allowed_mentions=discord.AllowedMentions.none(),
            )
            return
        except discord.HTTPException:
            self.processedMessageIds.add(message.id)

            await message.channel.send(
                embed=self.buildRolePaymentErrorEmbed(
                    title="Cấp role thất bại",
                    description=(
                        f"Người thanh toán: {senderMember.mention}\n"
                        f"Role cần cấp: {role.mention}\n"
                        "User đã thanh toán, nhưng bot cấp role thất bại.\n"
                        "Vui lòng liên hệ quản trị viên."
                    ),
                ),
                allowed_mentions=discord.AllowedMentions.none(),
            )
            return

        completeResult = self.roleShopPaymentService.completePayment(
            memberRolePurchaseId=paymentResult["memberRolePurchaseId"],
            paymentType=PaymentType.COWONCY.value,
            paymentAmount=cowoncyAmount,
        )

        if not completeResult["success"]:
            try:
                await senderMember.remove_roles(
                    role,
                    reason="Role shop payment database update failed",
                )
            except discord.HTTPException:
                pass

            self.processedMessageIds.add(message.id)

            await message.channel.send(
                embed=self.buildRolePaymentErrorEmbed(
                    title="Cập nhật giao dịch thất bại",
                    description=(
                        f"Người thanh toán: {senderMember.mention}\n"
                        f"Role đã cấp tạm thời: {role.mention}\n"
                        f"Nội dung lỗi: {completeResult['message']}"
                    ),
                ),
                allowed_mentions=discord.AllowedMentions.none(),
            )
            return

        self.processedMessageIds.add(message.id)

        await message.channel.send(
            embed=self.buildRolePaymentCompletedEmbed(
                senderMember=senderMember,
                role=role,
                cowoncyAmount=cowoncyAmount,
                expiredAt=completeResult["expiredAt"],
            ),
            allowed_mentions=discord.AllowedMentions.none(),
        )

    async def resolveGuildMember(
        self,
        guild: discord.Guild,
        userId: int,
    ):
        guildMember = guild.get_member(userId)

        if guildMember is not None:
            return guildMember

        try:
            return await guild.fetch_member(userId)
        except discord.NotFound:
            return None
        except discord.HTTPException:
            return None

    def extractOwoGiveInfo(self, content: str):
        normalizedContent = content.strip()

        match = re.search(
            r"\**💳\s*\|\s*<@!?(\d+)>\**\s*sent\s*\**([\d,]+)\s+cowoncy\**\s*to\s*\**<@!?(\d+)>\**!",
            normalizedContent,
            re.IGNORECASE,
        )

        if match is None:
            return None

        senderUserId = int(match.group(1))
        cowoncyAmount = int(match.group(2).replace(",", ""))
        receiverUserId = int(match.group(3))

        return {
            "senderUserId": senderUserId,
            "receiverUserId": receiverUserId,
            "cowoncyAmount": cowoncyAmount,
        }

    def buildThankYouMessage(
        self,
        senderMember: discord.Member,
        donatedCowoncy: int,
    ):
        return (
            "# <a:CS_decorate:1366286592758779995> Cảm Ơn Donate <a:CS_decorate:1366286658260963450>\n"
            f"Thay mặt {LOGO} cảm ơn {senderMember.mention} rất nhiều <a:CS_tim1:1466240640089325588>, "
            f"chúng tớ đã nhận được {donatedCowoncy:,} cowoncy, chúc bạn một ngày tốt lành."
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

    def buildRolePaymentFailedEmbed(
        self,
        senderMember: discord.Member,
        paymentResult: dict,
    ):
        embed = discord.Embed(
            title="Thanh toán role chưa hoàn tất",
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

    def buildRolePaymentCompletedEmbed(
        self,
        senderMember: discord.Member,
        role: discord.Role,
        cowoncyAmount: int,
        expiredAt,
    ):
        expiredAtText = expiredAt.strftime("%d/%m/%Y %H:%M")

        embed = discord.Embed(
            title="Thanh toán role thành công",
            description=(
                f"Người mua: {senderMember.mention}\n"
                f"Role đã mua: {role.mention}\n"
                f"Số tiền: **{cowoncyAmount:,}** <:OwO:1503021935724859473> owo\n"
                f"Hạn sử dụng đến: **{expiredAtText}**"
            ),
            color=discord.Color.green(),
        )

        return embed

    def buildRolePaymentErrorEmbed(
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


async def setup(bot):
    await bot.add_cog(OwoGiveEvent(bot))