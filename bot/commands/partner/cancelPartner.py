import discord
from discord.ext import commands

from bot.config.roles import MOD_ROLE_IDS
from bot.services.partner.cancelPartnerService import CancelPartnerService
from bot.views.partnerCancelView import PartnerCancelConfirmView


class CancelPartnerCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.cancelPartnerService = CancelPartnerService()

    @commands.command(name="cancelpn")
    async def cancelPartner(self, ctx: commands.Context, partnerId: int = None):
        if ctx.guild is None:
            await ctx.reply("Lệnh này chỉ dùng được trong server.")
            return

        if not self.hasPartnerPermission(ctx.author):
            await ctx.reply("Bạn không có quyền sử dụng lệnh này.")
            return

        if partnerId is None:
            await ctx.reply("Cách dùng: `cg cancelpn <partner_id>`")
            return

        result = self.cancelPartnerService.buildCancelPreview(partnerId)

        if not result["success"]:
            await ctx.reply(result["message"])
            return

        embed = discord.Embed(
            title="Xác nhận hủy server partner",
            description=(
                f"- Tên server: {result['guildName']}\n"
                f"- Người đại diện: {result['representativeText']}\n\n"
                "Bấm nút xác nhận bên dưới để hủy server partner."
            ),
            color=discord.Color.red(),
        )

        await ctx.reply(
            embed=embed,
            view=PartnerCancelConfirmView(
                bot=self.bot,
                partnerId=result["partnerId"],
                requestedByUserId=ctx.author.id,
            ),
            allowed_mentions=discord.AllowedMentions(
                users=True,
                roles=False,
                everyone=False,
            ),
        )

    def hasPartnerPermission(self, member):
        allowedRoleIds = {
            MOD_ROLE_IDS["mod"],
            MOD_ROLE_IDS["admin"],
            MOD_ROLE_IDS["owner"],
        }
        memberRoleIds = {role.id for role in member.roles}

        return not memberRoleIds.isdisjoint(allowedRoleIds)


async def setup(bot):
    await bot.add_cog(CancelPartnerCommand(bot))
