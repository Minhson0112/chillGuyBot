import discord
from discord.ext import commands

from bot.config.config import DONATE_REWARD_ROLES, LOGO
from bot.config.database import getDbSession
from bot.repository.owoDonateHistoryRepository import OwoDonateHistoryRepository


class MyDonate(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="mydn")
    async def myDonate(self, ctx):
        if ctx.guild is None:
            await ctx.send("Lệnh này chỉ dùng được trong server.")
            return

        with getDbSession() as session:
            owoDonateHistoryRepository = OwoDonateHistoryRepository(session)

            totalDonate = owoDonateHistoryRepository.getTotalDonateBySenderUserId(ctx.author.id)
            donateCount = owoDonateHistoryRepository.countDonateBySenderUserId(ctx.author.id)
            donateRank = owoDonateHistoryRepository.getDonateRankBySenderUserId(ctx.author.id)

        rewardRole = self.getHighestMatchedRewardRole(ctx.guild, totalDonate)

        embed = discord.Embed(
            title="Thông Tin Donate Của Bạn",
            description=f"{LOGO}\nCảm ơn bạn đã ủng hộ server.",
        )
        embed.add_field(
            name="Người dùng",
            value=ctx.author.mention,
            inline=False,
        )
        embed.add_field(
            name="Tổng donate",
            value=f"**{totalDonate:,}** cowoncy",
            inline=True,
        )
        embed.add_field(
            name="Số lần donate",
            value=str(donateCount),
            inline=True,
        )
        embed.add_field(
            name="Xếp hạng",
            value=f"#{donateRank}" if donateRank is not None else "Chưa có hạng",
            inline=True,
        )
        embed.add_field(
            name="Role donate hiện tại",
            value=rewardRole.mention if rewardRole is not None else "Chưa đạt mốc role",
            inline=False,
        )

        await ctx.send(embed=embed)

    def getHighestMatchedRewardRole(self, guild: discord.Guild, totalDonate: int):
        matchedRole = None

        for donateRewardRole in DONATE_REWARD_ROLES:
            if totalDonate >= donateRewardRole["minimumTotalDonate"]:
                role = guild.get_role(donateRewardRole["roleId"])
                if role is not None:
                    matchedRole = role

        return matchedRole


async def setup(bot):
    await bot.add_cog(MyDonate(bot))