from discord.ext import commands

from bot.services.farm.giftcodeService import GiftcodeService


class Giftcode(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.giftcodeService = GiftcodeService()

    @commands.command(name="giftcode")
    async def giftcode(self, ctx, code: str = None):
        if code is None:
            await ctx.reply("Cách dùng: `cg giftcode <code>`")
            return

        try:
            result = self.giftcodeService.claimGiftcode(
                userId=ctx.author.id,
                code=code,
            )

            await ctx.reply(result["message"])

        except Exception as e:
            print(f"Giftcode claim error: {e}")
            await ctx.reply("Đã xảy ra lỗi khi nhận giftcode.")


async def setup(bot):
    await bot.add_cog(Giftcode(bot))