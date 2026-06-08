import discord
from discord.ext import commands

from bot.config.emoji import LOGO, STRING, BLUEMOON
from bot.services.lotto.lottoTicketMessageService import LottoTicketMessageService
from bot.services.lotto.myLottoService import MyLottoService


class MyLottoCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.myLottoService = MyLottoService()
        self.lottoTicketMessageService = LottoTicketMessageService()

    @commands.command(name="mylotto")
    async def myLotto(self, ctx: commands.Context):
        if ctx.guild is None:
            return

        if not isinstance(ctx.author, discord.Member):
            return

        result = self.myLottoService.findMyLatestOpenEventTickets(
            userId=ctx.author.id,
        )

        if not result["success"]:
            await ctx.reply(
                f"{LOGO} {result['message']}",
                mention_author=False,
            )
            return

        if len(result["tickets"]) == 0:
            await ctx.reply(
                f"{LOGO} Bạn chưa có vé lotto nào trong event **{result['lottoEventName']}**.",
                mention_author=False,
            )
            return

        await ctx.reply(
            embed=self.lottoTicketMessageService.buildTicketListEmbed(
                member=ctx.author,
                title=f"{STRING} Vé lotto của bạn {BLUEMOON}",
                tickets=result["tickets"],
            ),
            mention_author=False,
        )


async def setup(bot):
    await bot.add_cog(MyLottoCommand(bot))
