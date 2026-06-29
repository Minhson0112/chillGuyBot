from discord.ext import commands

from bot.services.farm.farmBaseSkinUseService import FarmBaseSkinUseService


class UseSkinCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.farmBaseSkinUseService = FarmBaseSkinUseService()

    @commands.command(name="useskin")
    async def useSkin(self, ctx, inventoryId: int = None):
        if inventoryId is None:
            await ctx.reply("Cách dùng: `cg useskin <id kho skin>`")
            return

        try:
            result = self.farmBaseSkinUseService.useBaseSkin(
                userId=ctx.author.id,
                inventoryId=inventoryId,
            )

            await ctx.reply(result["message"])

        except Exception as e:
            print(f"Use base skin error: {e}")
            await ctx.reply("Đã xảy ra lỗi khi đổi base skin.")


async def setup(bot):
    await bot.add_cog(UseSkinCommand(bot))
