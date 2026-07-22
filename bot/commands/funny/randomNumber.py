import random

from discord.ext import commands

from bot.helper.numberFormatHelper import formatNumber


class RandomNumber(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="random")
    async def randomNumber(
        self,
        ctx: commands.Context,
        number1: str = None,
        number2: str = None,
    ):
        if ctx.guild is None:
            return

        if number1 is None or number2 is None:
            await ctx.reply(
                "Cách dùng: `cg random <số 1> <số 2>`",
                mention_author=False,
            )
            return

        try:
            firstNumber = int(number1)
            secondNumber = int(number2)
        except ValueError:
            await ctx.reply(
                "Số nhập vào phải là số nguyên.",
                mention_author=False,
            )
            return

        minNumber = min(firstNumber, secondNumber)
        maxNumber = max(firstNumber, secondNumber)
        result = random.randint(minNumber, maxNumber)

        await ctx.reply(
            (
                f"Random từ **{formatNumber(minNumber)}** đến "
                f"**{formatNumber(maxNumber)}**: **{formatNumber(result)}**"
            ),
            mention_author=False,
        )


async def setup(bot):
    await bot.add_cog(RandomNumber(bot))
