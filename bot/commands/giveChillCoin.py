import discord
from discord.ext import commands

from bot.services.farm.chillCoinGiveService import ChillCoinGiveService


class GiveChillCoinCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.chillCoinGiveService = ChillCoinGiveService()

    @commands.command(name="give")
    async def give(self, ctx, member: discord.Member = None, amount: int = None):
        if member is None or amount is None:
            await ctx.reply("Cách dùng: `cg give @user <số chill coin>`")
            return

        if member.bot:
            await ctx.reply("Không thể chuyển chill coin cho bot.")
            return

        try:
            giveResult = self.chillCoinGiveService.giveCoin(
                fromUserId=ctx.author.id,
                toUserId=member.id,
                amount=amount,
            )

            await ctx.reply(giveResult["message"])

        except Exception as e:
            print(f"Give chill coin error: {e}")
            await ctx.reply("Đã xảy ra lỗi khi chuyển chill coin.")


async def setup(bot):
    await bot.add_cog(GiveChillCoinCommand(bot))