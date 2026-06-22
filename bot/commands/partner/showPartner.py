import discord
from discord.ext import commands

from bot.config.roles import MOD_ROLE_IDS
from bot.services.partner.showPartnerService import ShowPartnerService
from bot.views.partner.partnerListPaginationView import PartnerListPaginationView


class ShowPartnerCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.showPartnerService = ShowPartnerService()

    @commands.command(name="showpn")
    async def showPartner(self, ctx: commands.Context):
        if ctx.guild is None:
            await ctx.reply("Lệnh này chỉ dùng được trong server.")
            return

        if not self.hasPartnerPermission(ctx.author):
            await ctx.reply("Bạn không có quyền sử dụng lệnh này.")
            return

        partners = self.showPartnerService.findAllPartners()
        view = PartnerListPaginationView(
            partners=partners,
            authorId=ctx.author.id,
        )

        await ctx.reply(
            embed=view.buildEmbed(),
            view=view,
            allowed_mentions=discord.AllowedMentions(
                users=False,
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
    await bot.add_cog(ShowPartnerCommand(bot))
