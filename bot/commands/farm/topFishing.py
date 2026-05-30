from datetime import datetime

import discord
from discord.ext import commands

from bot.services.farm.farmFishingRankingRenderService import FarmFishingRankingRenderService


class TopFishing(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.farmFishingRankingRenderService = FarmFishingRankingRenderService(bot)

    @commands.command(name="topf")
    async def topFishing(self, ctx, month: int = None):
        now = datetime.now()
        year = now.year

        if month is None:
            month = now.month

        if month < 1 or month > 12:
            await ctx.reply("Tháng không hợp lệ. Vui lòng nhập từ **1** đến **12**.")
            return

        try:
            renderResult = await self.farmFishingRankingRenderService.renderTopFishingByMonthToBuffer(
                guild=ctx.guild,
                year=year,
                month=month,
            )

            file = discord.File(
                renderResult["buffer"],
                filename="top_fishing.png",
            )

            content = f"BXH câu cá tháng **{month}/{year}**"

            if renderResult["rankingCount"] <= 0:
                content += "\nChưa có dữ liệu câu cá trong tháng này."

            await ctx.reply(
                content=content,
                file=file,
            )

        except FileNotFoundError as e:
            print(f"Fishing ranking asset file not found: {e}")
            await ctx.reply("Không tìm thấy ảnh asset để render bảng xếp hạng câu cá.")

        except Exception as e:
            print(f"Render fishing ranking error: {e}")
            await ctx.reply("Đã xảy ra lỗi khi render bảng xếp hạng câu cá.")


async def setup(bot):
    await bot.add_cog(TopFishing(bot))