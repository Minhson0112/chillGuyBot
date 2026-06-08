import discord
from discord.ext import commands

from bot.config.channel import PAYMENT_CHANNEL_ID
from bot.config.emoji import FARM_GAME_EMOJI
from bot.config.userId import OWNER_ID, TREASURER_MEMBER_ID_LIST
from bot.enums.chillCoinTransactionType import ChillCoinTransactionType
from bot.enums.memberPaymentTargetType import MemberPaymentTargetType
from bot.enums.paymentType import PaymentType
from bot.services.farm.chillCoinGiveService import ChillCoinGiveService
from bot.services.memberPayment.memberPaymentService import MemberPaymentService
from bot.services.roleShop.roleShopPaymentService import RoleShopPaymentService


class GiveChillCoinCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.chillCoinGiveService = ChillCoinGiveService()
        self.memberPaymentService = MemberPaymentService()
        self.roleShopPaymentService = RoleShopPaymentService()

    @commands.command(name="give")
    async def give(self, ctx: commands.Context, member: discord.Member = None, amount: int = None):
        if ctx.guild is None:
            return

        if member is None or amount is None:
            await ctx.reply(
                "Cách dùng: `cg give @user <số chill coin>`",
                mention_author=False,
            )
            return

        if member.bot:
            await ctx.reply(
                "Không thể chuyển chill coin cho bot.",
                mention_author=False,
            )
            return

        try:
            if ctx.channel.id == PAYMENT_CHANNEL_ID:
                await self.handlePayment(
                    ctx=ctx,
                    receiverMember=member,
                    amount=amount,
                )
                return

            giveResult = self.chillCoinGiveService.giveCoin(
                fromUserId=ctx.author.id,
                toUserId=member.id,
                amount=amount,
            )

            await ctx.reply(
                giveResult["message"],
                mention_author=False,
            )

        except Exception as e:
            print(f"Give chill coin error: {e}")

            await ctx.reply(
                "Đã xảy ra lỗi khi chuyển chill coin.",
                mention_author=False,
            )

    async def handlePayment(
        self,
        ctx: commands.Context,
        receiverMember: discord.Member,
        amount: int,
    ):
        if receiverMember.id != OWNER_ID and receiverMember.id not in TREASURER_MEMBER_ID_LIST:
            await ctx.reply(
                embed=self.buildPaymentErrorEmbed(
                    title="Thanh toán không hợp lệ",
                    description=(
                        "Kênh này chỉ dùng để thanh toán cho quản trị viên hoặc thủ quỹ."
                    ),
                ),
                allowed_mentions=discord.AllowedMentions.none(),
                mention_author=False,
            )
            return

        pendingPaymentResult = self.memberPaymentService.findPendingPaymentByUserId(ctx.author.id)

        if not pendingPaymentResult["success"]:
            await ctx.reply(
                embed=self.buildPaymentFailedEmbed(
                    ctx=ctx,
                    paymentResult=pendingPaymentResult,
                ),
                allowed_mentions=discord.AllowedMentions.none(),
                mention_author=False,
            )
            return

        paymentTargetType = pendingPaymentResult["paymentTargetType"]

        if paymentTargetType == MemberPaymentTargetType.ROLE_SHOP.value:
            await self.handleRolePayment(
                ctx=ctx,
                receiverMember=receiverMember,
                memberPaymentTransactionId=pendingPaymentResult["memberPaymentTransactionId"],
                amount=amount,
            )
            return

        await ctx.reply(
            embed=self.buildPaymentErrorEmbed(
                title="Thanh toán chưa được hỗ trợ",
                description=(
                    f"Người thanh toán: {ctx.author.mention}\n"
                    f"Loại giao dịch: `{paymentTargetType}`\n"
                    "Bot chưa hỗ trợ xử lý loại giao dịch này bằng chill coin."
                ),
            ),
            allowed_mentions=discord.AllowedMentions.none(),
            mention_author=False,
        )

    async def handleRolePayment(
        self,
        ctx: commands.Context,
        receiverMember: discord.Member,
        memberPaymentTransactionId: int,
        amount: int,
    ):
        paymentResult = self.roleShopPaymentService.verifyPayment(
            memberPaymentTransactionId=memberPaymentTransactionId,
            paymentType=PaymentType.CHILL_COIN.value,
            paymentAmount=amount,
        )

        if not paymentResult["success"]:
            await ctx.reply(
                embed=self.buildPaymentFailedEmbed(
                    ctx=ctx,
                    paymentResult=paymentResult,
                ),
                allowed_mentions=discord.AllowedMentions.none(),
                mention_author=False,
            )
            return

        giveResult = self.chillCoinGiveService.giveCoin(
            fromUserId=ctx.author.id,
            toUserId=receiverMember.id,
            amount=amount,
            transactionType=ChillCoinTransactionType.ROLE_PAYMENT.value,
            note="Role shop payment by chill coin",
            skipDailyReceiveLimit=True,
        )

        if not giveResult["success"]:
            await ctx.reply(
                embed=self.buildPaymentErrorEmbed(
                    title="Chuyển chill coin thất bại",
                    description=giveResult["message"],
                ),
                allowed_mentions=discord.AllowedMentions.none(),
                mention_author=False,
            )
            return

        role = ctx.guild.get_role(paymentResult["roleId"])

        if role is None:
            await ctx.reply(
                embed=self.buildPaymentErrorEmbed(
                    title="Thanh toán role cần xử lý thủ công",
                    description=(
                        f"Người thanh toán: {ctx.author.mention}\n"
                        "User đã chuyển chill coin thành công, nhưng role cần cấp không còn tồn tại trong server.\n"
                        "Vui lòng liên hệ quản trị viên."
                    ),
                ),
                allowed_mentions=discord.AllowedMentions.none(),
                mention_author=False,
            )
            return

        try:
            await ctx.author.add_roles(
                role,
                reason="Role shop payment completed by chill coin",
            )
        except discord.Forbidden:
            await ctx.reply(
                embed=self.buildPaymentErrorEmbed(
                    title="Bot không có quyền cấp role",
                    description=(
                        f"Người thanh toán: {ctx.author.mention}\n"
                        f"Role cần cấp: {role.mention}\n"
                        "User đã chuyển chill coin thành công, nhưng bot không có quyền cấp role này.\n"
                        "Vui lòng kiểm tra lại vị trí role của bot."
                    ),
                ),
                allowed_mentions=discord.AllowedMentions.none(),
                mention_author=False,
            )
            return
        except discord.HTTPException:
            await ctx.reply(
                embed=self.buildPaymentErrorEmbed(
                    title="Cấp role thất bại",
                    description=(
                        f"Người thanh toán: {ctx.author.mention}\n"
                        f"Role cần cấp: {role.mention}\n"
                        "User đã chuyển chill coin thành công, nhưng bot cấp role thất bại.\n"
                        "Vui lòng liên hệ quản trị viên."
                    ),
                ),
                allowed_mentions=discord.AllowedMentions.none(),
                mention_author=False,
            )
            return

        completeResult = self.roleShopPaymentService.completePayment(
            memberPaymentTransactionId=paymentResult["memberPaymentTransactionId"],
            paymentType=PaymentType.CHILL_COIN.value,
            paymentAmount=amount,
        )

        if not completeResult["success"]:
            try:
                await ctx.author.remove_roles(
                    role,
                    reason="Role shop payment database update failed",
                )
            except discord.HTTPException:
                pass

            await ctx.reply(
                embed=self.buildPaymentErrorEmbed(
                    title="Cập nhật giao dịch thất bại",
                    description=(
                        f"Người thanh toán: {ctx.author.mention}\n"
                        f"Role đã cấp tạm thời: {role.mention}\n"
                        f"Nội dung lỗi: {completeResult['message']}"
                    ),
                ),
                allowed_mentions=discord.AllowedMentions.none(),
                mention_author=False,
            )
            return

        await ctx.reply(
            embed=self.buildRolePaymentCompletedEmbed(
                member=ctx.author,
                role=role,
                chillCoinAmount=amount,
                expiredAt=completeResult["expiredAt"],
            ),
            allowed_mentions=discord.AllowedMentions.none(),
            mention_author=False,
        )

    def buildPaymentFailedEmbed(
        self,
        ctx: commands.Context,
        paymentResult: dict,
    ):
        embed = discord.Embed(
            title="Thanh toán role chưa hoàn tất",
            description=(
                f"Người thanh toán: {ctx.author.mention}\n"
                f"Nội dung: {paymentResult['message']}"
            ),
            color=discord.Color.orange(),
        )

        roleId = paymentResult.get("roleId")

        if roleId is not None:
            role = ctx.guild.get_role(roleId)

            if role is not None:
                embed.add_field(
                    name="Role đang chờ thanh toán",
                    value=role.mention,
                    inline=False,
                )

        return embed

    def buildRolePaymentCompletedEmbed(
        self,
        member: discord.Member,
        role: discord.Role,
        chillCoinAmount: int,
        expiredAt,
    ):
        chillCoinEmoji = FARM_GAME_EMOJI["chill_coin"]
        expiredAtText = expiredAt.strftime("%d/%m/%Y %H:%M")

        embed = discord.Embed(
            title="Thanh toán role thành công",
            description=(
                f"Người mua: {member.mention}\n"
                f"Role đã mua: {role.mention}\n"
                f"Số tiền: **{self.formatNumber(chillCoinAmount)}** {chillCoinEmoji}\n"
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

    def formatNumber(self, number: int):
        return f"{number:,}"


async def setup(bot):
    await bot.add_cog(GiveChillCoinCommand(bot))
