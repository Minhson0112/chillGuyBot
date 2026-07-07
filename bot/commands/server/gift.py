import discord
from discord.ext import commands

from bot.helper.numberFormatHelper import formatNumber
from bot.services.serverItem.serverItemGiftService import ServerItemGiftService


class GiftCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.serverItemGiftService = ServerItemGiftService()

    @commands.command(name="gift")
    async def gift(
        self,
        ctx: commands.Context,
        member: discord.Member = None,
        inventoryId: int = None,
        quantity: int = 1,
    ):
        if ctx.guild is None:
            return

        if member is None or inventoryId is None:
            await ctx.reply(
                "Cách dùng: `cg gift @user <id_item_trong_kho> [số_lượng]`",
                mention_author=False,
            )
            return

        if member.bot:
            await ctx.reply(
                "Bạn không thể tặng item cho bot.",
                mention_author=False,
            )
            return

        result = self.serverItemGiftService.giftItem(
            giverUserId=ctx.author.id,
            receiverUserId=member.id,
            inventoryId=inventoryId,
            quantity=quantity,
        )

        if not result["success"]:
            await ctx.reply(
                result["message"],
                mention_author=False,
            )
            return

        await ctx.reply(
            embed=self.buildGiftEmbed(
                giver=ctx.author,
                receiver=member,
                result=result,
            ),
            allowed_mentions=discord.AllowedMentions(
                users=True,
                roles=False,
                everyone=False,
            ),
            mention_author=False,
        )

    def buildGiftEmbed(
        self,
        giver: discord.Member,
        receiver: discord.Member,
        result: dict,
    ):
        embed = discord.Embed(
            title="Tặng item thành công",
            description=(
                f"{giver.mention} đã tặng {receiver.mention} "
                f"{self.buildItemText(result['itemName'], result['itemEmoji'])} "
                f"x**{formatNumber(result['quantity'])}**.\n"
                f"Điểm thân mật tăng: **{formatNumber(result['intimacyPointsGained'])}**\n"
                f"Tổng điểm thân mật hiện tại: **{formatNumber(result['totalIntimacyPoints'])}**"
            ),
            color=discord.Color.pink(),
        )

        return embed

    def buildItemText(self, itemName: str, itemEmoji: str | None):
        if itemEmoji is None:
            return f"**{itemName}**"

        return f"{itemEmoji} **{itemName}**"


async def setup(bot):
    await bot.add_cog(GiftCommand(bot))
