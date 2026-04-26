from discord.ext import commands

from bot.config.database import getDbSession
from bot.config.emoji import FARM_GAME_EMOJI
from bot.repository.memberRepository import MemberRepository


class CashCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="cash")
    async def cash(self, ctx):
        with getDbSession() as session:
            memberRepository = MemberRepository(session)
            member = memberRepository.findByUserId(ctx.author.id)

            if member is None:
                await ctx.reply("Không tìm thấy dữ liệu member của bạn.")
                return

            chillCoinEmoji = FARM_GAME_EMOJI["chill_coin"]
            chillCoin = self.formatNumber(member.chill_coin)

            await ctx.reply(
                f"{ctx.author.mention} ơi, bạn hiện có {chillCoinEmoji} **{chillCoin}** chill coin."
            )

    def formatNumber(self, number: int):
        return f"{number:,}"


async def setup(bot):
    await bot.add_cog(CashCommand(bot))