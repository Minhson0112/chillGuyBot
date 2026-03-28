import re

import discord
from discord.ext import commands

from bot.config.config import WORDLE_CHANNEL_ID
from bot.services.wordle.wordleGameService import WordleGameService


class WordleEvent(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.wordleGameService = WordleGameService()

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return

        if message.guild is None:
            return

        if message.channel.id != WORDLE_CHANNEL_ID:
            return

        guessedWord = message.content.strip()

        if not re.fullmatch(r"[a-zA-Z]{5}", guessedWord):
            return

        result = self.wordleGameService.guessWord(guessedWord, message.author.id)

        if not result["success"]:
            await message.channel.send(result["message"])
            return

        await message.channel.send(result["guessEmojiRow"])

        if result["isCompleted"]:
            await message.channel.send(
                f"Chúc mừng **{message.author.mention}** đã hoàn thành từ khóa **{result['completedWord']}**.\n"
                f"Từ mới đã được bắt đầu, độ dài từ khóa mới là **{result['nextWordLength']}** ký tự."
            )

async def setup(bot):
    await bot.add_cog(WordleEvent(bot))
