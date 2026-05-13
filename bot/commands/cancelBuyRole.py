import discord
from discord.ext import commands

from bot.config.emoji import LOGO
from bot.services.roleShop.roleShopPurchaseCancelService import RoleShopPurchaseCancelService


class CancelBuyRoleCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.roleShopPurchaseCancelService = RoleShopPurchaseCancelService()

    @commands.command(name="cancelbuyrole")
    async def cancelBuyRole(self, ctx: commands.Context):
        if ctx.guild is None:
            return

        result = self.roleShopPurchaseCancelService.cancelPendingPurchases(
            userId=ctx.author.id,
        )

        if not result["success"]:
            await ctx.reply(
                f"{LOGO} {result['message']}",
                mention_author=False,
            )
            return

        roleTextList = []

        for roleId in result["cancelledRoleIds"]:
            role = ctx.guild.get_role(roleId)

            if role is not None:
                roleTextList.append(role.mention)
            else:
                roleTextList.append(f"`{roleId}`")

        roleText = ", ".join(roleTextList)

        await ctx.reply(
            content=ctx.author.mention,
            embed=self.buildCancelBuyRoleEmbed(
                message=result["message"],
                roleText=roleText,
            ),
            allowed_mentions=discord.AllowedMentions(
                users=True,
                roles=False,
                everyone=False,
            ),
            mention_author=False,
        )

    def buildCancelBuyRoleEmbed(
        self,
        message: str,
        roleText: str,
    ):
        embed = discord.Embed(
            title="Đã hủy giao dịch mua role",
            description=(
                f"{message}\n\n"
                f"Role đã hủy: {roleText}"
            ),
            color=discord.Color.orange(),
        )

        return embed


async def setup(bot):
    await bot.add_cog(CancelBuyRoleCommand(bot))