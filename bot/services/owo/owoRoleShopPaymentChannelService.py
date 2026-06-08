import discord

from bot.enums.paymentType import PaymentType
from bot.services.roleShop.roleShopPaymentService import RoleShopPaymentService


class OwoRoleShopPaymentChannelService:
    def __init__(self):
        self.roleShopPaymentService = RoleShopPaymentService()

    async def handleRoleShopPayment(
        self,
        message: discord.Message,
        senderMember: discord.Member,
        memberPaymentTransactionId: int,
        cowoncyAmount: int,
    ):
        paymentResult = self.roleShopPaymentService.verifyPayment(
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

        role = message.guild.get_role(paymentResult["roleId"])

        if role is None:
            await message.channel.send(
                embed=self.buildPaymentErrorEmbed(
                    title="Thanh toán role cần xử lý thủ công",
                    description=(
                        f"Người thanh toán: {senderMember.mention}\n"
                        "User đã thanh toán, nhưng role cần cấp không còn tồn tại trong server.\n"
                        "Vui lòng liên hệ quản trị viên."
                    ),
                ),
                allowed_mentions=discord.AllowedMentions.none(),
            )
            return True

        try:
            await senderMember.add_roles(
                role,
                reason="Role shop payment completed",
            )
        except discord.Forbidden:
            await message.channel.send(
                embed=self.buildPaymentErrorEmbed(
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
            return True
        except discord.HTTPException:
            await message.channel.send(
                embed=self.buildPaymentErrorEmbed(
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
            return True

        completeResult = self.roleShopPaymentService.completePayment(
            memberPaymentTransactionId=paymentResult["memberPaymentTransactionId"],
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

            await message.channel.send(
                embed=self.buildPaymentErrorEmbed(
                    title="Cập nhật giao dịch thất bại",
                    description=(
                        f"Người thanh toán: {senderMember.mention}\n"
                        f"Role đã cấp tạm thời: {role.mention}\n"
                        f"Nội dung lỗi: {completeResult['message']}"
                    ),
                ),
                allowed_mentions=discord.AllowedMentions.none(),
            )
            return True

        await message.channel.send(
            embed=self.buildRolePaymentCompletedEmbed(
                senderMember=senderMember,
                role=role,
                cowoncyAmount=cowoncyAmount,
                expiredAt=completeResult["expiredAt"],
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
