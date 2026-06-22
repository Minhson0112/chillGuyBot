from discord.ext import commands

from bot.services.server.serverInviteListService import ServerInviteListService
from bot.views.server.serverInvitePaginationView import ServerInvitePaginationView


class ListInvitesCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.serverInviteListService = ServerInviteListService()

    @commands.command(name="listinv", aliases=["invites"])
    async def listInvites(self, ctx, page: int = 1):
        if ctx.guild is None:
            await ctx.send("Lệnh này chỉ dùng được trong server.")
            return

        if page < 1:
            await ctx.reply("Trang không hợp lệ. Hãy nhập số trang lớn hơn hoặc bằng 1.", mention_author=False)
            return

        invites = self.serverInviteListService.findAllInvites()
        view = ServerInvitePaginationView(
            invites=invites,
            authorId=ctx.author.id,
            currentPage=page,
            perPage=10,
        )

        await ctx.reply(
            embed=view.buildEmbed(ctx.guild),
            view=view,
            mention_author=False,
        )


async def setup(bot):
    await bot.add_cog(ListInvitesCommand(bot))
