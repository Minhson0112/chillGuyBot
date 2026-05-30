from discord.ext import commands

from bot.services.farm.farmToolUseService import FarmToolUseService


class Use(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.farmToolUseService = FarmToolUseService()

    @commands.command(name="use")
    async def use(
        self,
        ctx: commands.Context,
        userToolId: int = None,
    ):
        if ctx.guild is None:
            return

        if userToolId is None:
            await ctx.reply(
                f"Hãy nhập ID dụng cụ cần dùng.\n"
                f"Ví dụ: `cg use 18`"
            )
            return

        result = self.farmToolUseService.useTool(
            userId=ctx.author.id,
            userToolId=userToolId,
        )

        await ctx.reply(f"{result['message']}")


async def setup(bot):
    await bot.add_cog(Use(bot))