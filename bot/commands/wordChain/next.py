from discord.ext import commands

from bot.config.channel import WORD_CHAIN_CHANNEL_ID
from bot.services.wordChain.wordChainStartupService import WordChainStartupService


class WordChainNext(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.wordChainStartupService = WordChainStartupService()

    @commands.command(name="next")
    async def nextWord(self, ctx: commands.Context):
        if ctx.guild is None:
            await ctx.reply(
                "Lệnh này chỉ dùng được trong server.",
                mention_author=False,
            )
            return

        if ctx.channel.id != WORD_CHAIN_CHANNEL_ID:
            return

        gameState = await self.wordChainStartupService.startNewGame(self.bot)

        if gameState is None:
            await ctx.reply(
                "Không thể tạo từ nối chữ mới.",
                mention_author=False,
            )
            return

        await ctx.message.add_reaction("✅")


async def setup(bot):
    await bot.add_cog(WordChainNext(bot))
