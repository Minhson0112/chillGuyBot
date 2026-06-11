from datetime import datetime, timedelta, timezone

from discord.ext import commands

from bot.config.database import getDbSession
from bot.repository.mergeGamePlayHistoryRepository import MergeGamePlayHistoryRepository
from bot.services.mergeGame.mergeGameRankingComponentService import MergeGameRankingComponentService


class TopMergeGame(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.gmt7 = timezone(timedelta(hours=7))
        self.mergeGameRankingComponentService = MergeGameRankingComponentService(bot)

    @commands.command(name="topm")
    async def topMergeGame(self, ctx):
        if ctx.guild is None:
            await ctx.reply("lệnh này chỉ có thể sử dụng trong server.", mention_author=False)
            return

        nowGmt7 = datetime.now(self.gmt7)
        targetYear = nowGmt7.year
        targetMonth = nowGmt7.month

        with getDbSession() as session:
            mergeGamePlayHistoryRepository = MergeGamePlayHistoryRepository(session)
            topMembers = mergeGamePlayHistoryRepository.findTopMembersByMonth(
                targetYear,
                targetMonth,
                5,
            )

        await self.mergeGameRankingComponentService.sendTopMembersMessage(
            ctx,
            topMembers,
            targetYear,
            targetMonth,
        )


async def setup(bot):
    await bot.add_cog(TopMergeGame(bot))
