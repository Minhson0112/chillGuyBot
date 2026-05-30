import discord
from discord.ext import commands

from bot.config.emoji import LOGO
from bot.services.farm.farmInventoryRenderService import FarmInventoryRenderService


class ToolBagCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.farmInventoryRenderService = FarmInventoryRenderService()

    @commands.command(name="toolbag")
    async def toolBag(
        self,
        ctx: commands.Context,
        page: int = 1,
    ):
        if ctx.guild is None:
            return

        result = self.farmInventoryRenderService.renderToolBagPageToBuffer(
            userId=ctx.author.id,
            memberDisplayName=ctx.author.display_name,
            page=page,
        )

        file = discord.File(
            fp=result["buffer"],
            filename="toolbag.png",
        )

        await ctx.reply(
            content=(
                f"{LOGO} Tool Bag của **{ctx.author.display_name}** "
                f"({result['currentPage']}/{result['totalPage']})"
            ),
            file=file,
        )


async def setup(bot):
    await bot.add_cog(ToolBagCommand(bot))