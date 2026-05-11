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
            await ctx.reply(f"{LOGO} {result['message']}")
            return

        roleMentions = []

        for roleId in result["cancelledRoleIds"]:
            role = ctx.guild.get_role(roleId)

            if role is not None:
                roleMentions.append(role.mention)
            else:
                roleMentions.append(f"`{roleId}`")

        roleText = ", ".join(roleMentions)

        await ctx.reply(
            f"{LOGO} {result['message']}\n"
            f"Role đã hủy: {roleText}"
        )


async def setup(bot):
    await bot.add_cog(CancelBuyRoleCommand(bot))