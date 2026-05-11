import discord
from discord.ext import commands

from bot.config.channel import PAYMENT_CHANNEL_ID
from bot.config.emoji import FARM_GAME_EMOJI
from bot.config.userId import OWNER_ID, TREASURER_MEMBER_ID_LIST
from bot.enums.paymentType import PaymentType
from bot.services.farm.chillCoinGiveService import ChillCoinGiveService
from bot.services.roleShop.roleShopPaymentService import RoleShopPaymentService


class GiveChillCoinCommand(commands.Cog):
    ROLE_PAYMENT_TRANSACTION_TYPE = "role_payment"

    def __init__(self, bot):
        self.bot = bot
        self.chillCoinGiveService = ChillCoinGiveService()
        self.roleShopPaymentService = RoleShopPaymentService()

    @commands.command(name="give")
    async def give(self, ctx, member: discord.Member = None, amount: int = None):
        if member is None or amount is None:
            await ctx.reply("Cách dùng: `cg give @user <số chill coin>`")
            return

        if member.bot:
            await ctx.reply("Không thể chuyển chill coin cho bot.")
            return

        try:
            if ctx.channel.id == PAYMENT_CHANNEL_ID:
                await self.handleRolePayment(
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

            await ctx.reply(giveResult["message"])

        except Exception as e:
            print(f"Give chill coin error: {e}")
            await ctx.reply("Đã xảy ra lỗi khi chuyển chill coin.")

    async def handleRolePayment(
        self,
        ctx: commands.Context,
        receiverMember: discord.Member,
        amount: int,
    ):
        if receiverMember.id != OWNER_ID and receiverMember.id not in TREASURER_MEMBER_ID_LIST:
            await ctx.reply("Kênh này chỉ dùng để thanh toán role cho quản trị viên hoặc thủ quỹ.")
            return

        paymentResult = self.roleShopPaymentService.verifyPayment(
            userId=ctx.author.id,
            paymentType=PaymentType.CHILL_COIN.value,
            paymentAmount=amount,
        )

        if not paymentResult["success"]:
            await ctx.reply(
                self.buildRolePaymentFailedMessage(
                    ctx=ctx,
                    paymentResult=paymentResult,
                )
            )
            return

        giveResult = self.chillCoinGiveService.giveCoin(
            fromUserId=ctx.author.id,
            toUserId=receiverMember.id,
            amount=amount,
            transactionType=self.ROLE_PAYMENT_TRANSACTION_TYPE,
            note="Role shop payment by chill coin",
            skipDailyReceiveLimit=True,
        )

        if not giveResult["success"]:
            await ctx.reply(giveResult["message"])
            return

        role = ctx.guild.get_role(paymentResult["roleId"])

        if role is None:
            await ctx.reply(
                f"{ctx.author.mention} đã chuyển chill coin thành công, nhưng role cần cấp không còn tồn tại trong server. "
                f"Vui lòng liên hệ quản trị viên."
            )
            return

        try:
            await ctx.author.add_roles(
                role,
                reason="Role shop payment completed by chill coin",
            )
        except discord.Forbidden:
            await ctx.reply(
                f"{ctx.author.mention} đã chuyển chill coin thành công, nhưng bot không có quyền cấp role {role.mention}. "
                f"Vui lòng liên hệ quản trị viên."
            )
            return
        except discord.HTTPException:
            await ctx.reply(
                f"{ctx.author.mention} đã chuyển chill coin thành công, nhưng bot cấp role {role.mention} thất bại. "
                f"Vui lòng liên hệ quản trị viên."
            )
            return

        completeResult = self.roleShopPaymentService.completePayment(
            memberRolePurchaseId=paymentResult["memberRolePurchaseId"],
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
                f"{ctx.author.mention} {completeResult['message']}"
            )
            return

        await ctx.reply(
            self.buildRolePaymentCompletedMessage(
                member=ctx.author,
                role=role,
                chillCoinAmount=amount,
                expiredAt=completeResult["expiredAt"],
            )
        )

    def buildRolePaymentFailedMessage(
        self,
        ctx: commands.Context,
        paymentResult: dict,
    ):
        roleText = ""
        roleId = paymentResult.get("roleId")

        if roleId is not None:
            role = ctx.guild.get_role(roleId)

            if role is not None:
                roleText = f"\nRole đang chờ thanh toán: {role.mention}"

        return (
            f"{ctx.author.mention} {paymentResult['message']}"
            f"{roleText}"
        )

    def buildRolePaymentCompletedMessage(
        self,
        member: discord.Member,
        role: discord.Role,
        chillCoinAmount: int,
        expiredAt,
    ):
        chillCoinEmoji = FARM_GAME_EMOJI["chill_coin"]
        expiredAtText = expiredAt.strftime("%d/%m/%Y %H:%M")

        return (
            f"{member.mention} đã thanh toán **{self.formatNumber(chillCoinAmount)}** {chillCoinEmoji} thành công.\n"
            f"Bạn đã được cấp role {role.mention}.\n"
            f"Role sẽ hết hạn vào: **{expiredAtText}**."
        )

    def formatNumber(self, number: int):
        return f"{number:,}"


async def setup(bot):
    await bot.add_cog(GiveChillCoinCommand(bot))