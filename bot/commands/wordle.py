import discord
from discord.ext import commands

from bot.config.channel import WORDLE_CHANNEL_ID
from bot.services.wordle.wordleGameService import WordleGameService


class Wordle(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.wordleGameService = WordleGameService()

    @commands.command(name="w")
    async def guessWord(self, ctx, guessedWord: str):
        if ctx.guild is None:
            await ctx.send("Lệnh này chỉ dùng được trong server.")
            return

        if ctx.channel.id != WORDLE_CHANNEL_ID:
            return

        result = self.wordleGameService.guessWord(guessedWord, ctx.author.id)

        if not result["success"]:
            await ctx.send(result["message"])
            return

        await ctx.send(result["guessEmojiRow"])

        if result["isCompleted"]:
            await ctx.send(
                f"Chúc mừng **{ctx.author.display_name}** đã hoàn thành từ khóa **{result['completedWord']}**.\n"
                f"Từ mới đã được bắt đầu, độ dài từ khóa mới là **{result['nextWordLength']}** ký tự."
            )


async def setup(bot):
    await bot.add_cog(Wordle(bot))