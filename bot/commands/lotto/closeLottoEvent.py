import discord
from discord.ext import commands

from bot.config.emoji import LOGO
from bot.config.roles import MOD_ROLE_IDS
from bot.services.lotto.closeLottoEventService import CloseLottoEventService


class CloseLottoEventCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.closeLottoEventService = CloseLottoEventService()

    @commands.command(name="closelottoevent")
    async def closeLottoEvent(self, ctx: commands.Context, lottoEventId: int = None):
        if ctx.guild is None:
            return

        if lottoEventId is None:
            await ctx.reply(
                f"{LOGO} Cách dùng: `cg closelottoevent <lotto_event_id>`",
                mention_author=False,
            )
            return

        if not self.hasEventPermission(ctx.author):
            await ctx.reply(
                f"{LOGO} Bạn không có quyền sử dụng lệnh này.",
                mention_author=False,
            )
            return

        result = self.closeLottoEventService.closeLottoEvent(
            lottoEventId=lottoEventId,
        )

        if not result["success"]:
            await ctx.reply(
                f"{LOGO} {result['message']}",
                mention_author=False,
            )
            return

        await ctx.reply(
            f"{LOGO} {result['message']}\n"
            f"Event: **#{result['lottoEventId']} - {result['lottoEventName']}**",
            mention_author=False,
        )

    def hasEventPermission(self, member):
        if not isinstance(member, discord.Member):
            return False

        memberRoleIds = {role.id for role in member.roles}
        allowedRoleIds = {
            MOD_ROLE_IDS["admin"],
            MOD_ROLE_IDS["owner"],
        }

        return not memberRoleIds.isdisjoint(allowedRoleIds)


async def setup(bot):
    await bot.add_cog(CloseLottoEventCommand(bot))
