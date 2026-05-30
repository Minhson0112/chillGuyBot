from datetime import datetime, timedelta, timezone

import discord
from discord.ext import commands

from bot.config.database import getDbSession
from bot.repository.memberDailyActivityRepository import MemberDailyActivityRepository
from bot.services.memberActivity.memberStaffChatRankingImageService import MemberStaffChatRankingImageService


class TopChatStaff(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.gmt7 = timezone(timedelta(hours=7))
        self.memberStaffChatRankingImageService = MemberStaffChatRankingImageService(bot)

    @commands.command(name="topcstaff")
    async def topChatStaff(self, ctx, month: int | None = None):
        nowGmt7 = datetime.now(self.gmt7)

        targetYear = nowGmt7.year
        targetMonth = month if month is not None else nowGmt7.month

        if targetMonth < 1 or targetMonth > 12:
            await ctx.reply("Tháng không hợp lệ. Hãy nhập từ 1 đến 12.", mention_author=False)
            return

        with getDbSession() as session:
            memberDailyActivityRepository = MemberDailyActivityRepository(session)
            topMembers = memberDailyActivityRepository.findTopLevelChatStaffMembersByMonth(
                targetYear,
                targetMonth,
                10,
            )

        imageBuffer = await self.memberStaffChatRankingImageService.buildRankingImage(
            topMembers,
            ctx.guild,
        )

        file = discord.File(
            fp=imageBuffer,
            filename="staff_chat_ranking.png",
        )

        await ctx.reply(
            content=f"Bảng xếp hạng chat staff tháng **{targetMonth}/{targetYear}**",
            file=file,
            mention_author=False,
        )


async def setup(bot):
    await bot.add_cog(TopChatStaff(bot))