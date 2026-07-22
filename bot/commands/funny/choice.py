import random

from discord.ext import commands


class Choice(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="choice")
    async def choice(
        self,
        ctx: commands.Context,
        *,
        options: str = None,
    ):
        if ctx.guild is None:
            return

        if options is None:
            await ctx.reply(
                "Cách dùng: `cg choice gà, vịt, chó, mèo`",
                mention_author=False,
            )
            return

        choices = [
            option.strip()
            for option in options.split(",")
            if option.strip() != ""
        ]

        if len(choices) < 2:
            await ctx.reply(
                "Bạn cần nhập ít nhất 2 lựa chọn, cách nhau bằng dấu `,`.",
                mention_author=False,
            )
            return

        result = random.choice(choices)

        await ctx.reply(
            f"Mình chọn: **{result}**",
            mention_author=False,
        )


async def setup(bot):
    await bot.add_cog(Choice(bot))
