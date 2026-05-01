from datetime import datetime, timedelta, timezone

import discord
from discord.ext import commands

from bot.config.database import getDbSession
from bot.repository.memberDailyActivityRepository import MemberDailyActivityRepository
from bot.services.memberActivity.memberChatRankingImageService import MemberChatRankingImageService


class TopChat(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.gmt7 = timezone(timedelta(hours=7))
        self.memberChatRankingImageService = MemberChatRankingImageService()

    @commands.command(name="topc")
    async def topChat(self, ctx, month: int | None = None):
        nowGmt7 = datetime.now(self.gmt7)

        targetYear = nowGmt7.year
        targetMonth = month if month is not None else nowGmt7.month

        if targetMonth < 1 or targetMonth > 12:
            await ctx.reply("Tháng không hợp lệ. Hãy nhập từ 1 đến 12.", mention_author=False)
            return

        with getDbSession() as session:
            memberDailyActivityRepository = MemberDailyActivityRepository(session)
            topMembers = memberDailyActivityRepository.findTopLevelChatMembersByMonth(
                targetYear,
                targetMonth,
                10,
            )

        imageBuffer = self.memberChatRankingImageService.buildRankingImage(topMembers)

        file = discord.File(
            fp=imageBuffer,
            filename="chat_ranking.png",
        )

        await ctx.reply(
            content=f"Bảng xếp hạng chat tháng **{targetMonth}/{targetYear}**",
            file=file,
            mention_author=False,
        )


async def setup(bot):
    await bot.add_cog(TopChat(bot))