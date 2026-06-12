import discord
from discord.ext import commands

from bot.services.mergeGame.mergeGameRankingComponentService import MergeGameRankingComponentService


class TopMergeGame(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.mergeGameRankingComponentService = MergeGameRankingComponentService(bot)

    @commands.command(name="topm")
    async def topMergeGame(self, ctx):
        if ctx.guild is None:
            await ctx.reply("lệnh này chỉ có thể sử dụng trong server.", mention_author=False)
            return

        await self.mergeGameRankingComponentService.sendTopMembersMessage(ctx)

    @commands.Cog.listener()
    async def on_interaction(self, interaction: discord.Interaction):
        if interaction.type != discord.InteractionType.component:
            return

        customId = self.getCustomId(interaction)

        if customId is None:
            return

        customIdPrefix = self.mergeGameRankingComponentService.CUSTOM_ID_PREFIX

        if not customId.startswith(f"{customIdPrefix}:"):
            return

        rankingType = customId.removeprefix(f"{customIdPrefix}:")

        if rankingType not in {
            self.mergeGameRankingComponentService.RANKING_TYPE_SCORE,
            self.mergeGameRankingComponentService.RANKING_TYPE_SUN,
        }:
            return

        if interaction.guild is None:
            await interaction.response.send_message(
                "Lệnh này chỉ có thể sử dụng trong server.",
                ephemeral=True,
            )
            return

        if interaction.message is None or interaction.channel is None:
            await interaction.response.send_message(
                "Không thể cập nhật bảng xếp hạng này.",
                ephemeral=True,
            )
            return

        await interaction.response.defer()
        await self.mergeGameRankingComponentService.updateTopMembersMessage(
            interaction,
            rankingType,
        )

    def getCustomId(self, interaction: discord.Interaction):
        if interaction.data is None:
            return None

        return interaction.data.get("custom_id")


async def setup(bot):
    await bot.add_cog(TopMergeGame(bot))
