from datetime import datetime

import discord
from discord.ext import commands

from bot.services.farm.farmTrainRankingRenderService import FarmTrainRankingRenderService


class TopTrain(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.farmTrainRankingRenderService = FarmTrainRankingRenderService(bot)

    @commands.command(name="topt")
    async def topTrain(self, ctx, month: int = None):
        now = datetime.now()
        year = now.year

        if month is None:
            month = now.month

        if month < 1 or month > 12:
            await ctx.reply("Tháng không hợp lệ. Vui lòng nhập từ **1** đến **12**.")
            return

        try:
            renderResult = await self.farmTrainRankingRenderService.renderTopTrainByMonthToBuffer(
                guild=ctx.guild,
                year=year,
                month=month,
            )

            file = discord.File(
                renderResult["buffer"],
                filename="top_train.png",
            )

            content = f"BXH hoàn thành đơn tàu hỏa tháng **{month}/{year}**"

            if renderResult["rankingCount"] <= 0:
                content += "\nChưa có dữ liệu hoàn thành đơn tàu hỏa trong tháng này."

            await ctx.reply(
                content=content,
                file=file,
            )

        except FileNotFoundError as e:
            print(f"Train ranking asset file not found: {e}")
            await ctx.reply("Không tìm thấy ảnh asset để render bảng xếp hạng tàu hỏa.")

        except Exception as e:
            print(f"Render train ranking error: {e}")
            await ctx.reply("Đã xảy ra lỗi khi render bảng xếp hạng tàu hỏa.")


async def setup(bot):
    await bot.add_cog(TopTrain(bot))