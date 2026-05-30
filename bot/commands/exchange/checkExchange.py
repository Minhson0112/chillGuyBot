from discord.ext import commands

from bot.config.emoji import FARM_GAME_EMOJI
from bot.services.exchange.chillCoinExchangeCowoncyService import ChillCoinExchangeCowoncyService
from bot.services.exchange.owoExchangeCoinService import OwoExchangeCoinService


class CheckExchangeCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.chillCoinExchangeCowoncyService = ChillCoinExchangeCowoncyService()
        self.owoExchangeCoinService = OwoExchangeCoinService()

    @commands.command(name="checkexchange")
    async def checkExchange(self, ctx: commands.Context):
        if ctx.guild is None:
            return

        cowoncyToChillCoinStatus = self.owoExchangeCoinService.getExchangeStatus(
            senderUserId=ctx.author.id,
        )
        chillCoinToCowoncyStatus = self.chillCoinExchangeCowoncyService.getExchangeStatus(
            receiverUserId=ctx.author.id,
        )
        chillCoinEmoji = FARM_GAME_EMOJI["chill_coin"]

        await ctx.reply(
            (
                f"{ctx.author.mention} hạn mức đổi tiền hiện tại:\n"
                f"**Cowoncy -> chill coin**\n"
                f"Còn đổi được **{cowoncyToChillCoinStatus['remainingCowoncyAmount']:,}** <:OwO:1503021935724859473> "
                f"thành **{cowoncyToChillCoinStatus['remainingChillCoinAmount']:,}** {chillCoinEmoji}.\n"
                f"Reset tiếp theo: **{self.formatResetAt(cowoncyToChillCoinStatus['resetAt'])}**\n\n"
                f"**Chill coin -> cowoncy**\n"
                f"Còn đổi được **{chillCoinToCowoncyStatus['remainingChillCoinAmount']:,}** {chillCoinEmoji} "
                f"thành **{chillCoinToCowoncyStatus['remainingCowoncyAmount']:,}** <:OwO:1503021935724859473>.\n"
                f"Reset tiếp theo: **{self.formatResetAt(chillCoinToCowoncyStatus['resetAt'])}**"
            ),
            mention_author=False,
        )

    def formatResetAt(self, resetAt):
        return resetAt.strftime("%d/%m/%Y %H:%M (GMT+7)")


async def setup(bot):
    await bot.add_cog(CheckExchangeCommand(bot))
