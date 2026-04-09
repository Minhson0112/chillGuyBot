import re

import discord
from discord.ext import commands

from bot.config.config import WORDLE_CHANNEL_ID
from bot.services.wordle.wordleDictionaryCacheService import wordleDictionaryCacheService
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

        if not wordleDictionaryCacheService.hasWord(guessedWord):
            await message.channel.send(
                f"Từ **{guessedWord.upper()}** không có nghĩa hoặc không tồn tại trong cơ sở dữ liệu của bot."
            )
            return

        result = await self.wordleGameService.guessWord(guessedWord, message.author.id)

        if not result["success"]:
            await message.channel.send(result["message"])
            return

        await message.channel.send(result["guessEmojiRow"])

        if result["isCompleted"]:
            completedDefinitionVi = result.get("completedDefinitionVi")
            completedDefinitionEn = result.get("completedDefinitionEn")

            definitionText = completedDefinitionVi or completedDefinitionEn or "Không có định nghĩa cho từ này."

            embed = discord.Embed(
                title=f"{message.author.display_name} đã mở được từ {result['completedWord']}",
                description=definitionText,
            )

            embed.add_field(
                name="Người hoàn thành",
                value=message.author.mention,
                inline=False,
            )

            embed.set_footer(
                text=f"Từ mới đã được bắt đầu • Độ dài từ mới: {result['nextWordLength']} ký tự"
            )

            await message.channel.send(embed=embed)


async def setup(bot):
    await bot.add_cog(WordleEvent(bot))