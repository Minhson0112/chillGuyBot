import re

import discord
from discord.ext import commands

from bot.config.channel import WORDLE_CHANNEL_ID
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
            definitionEntries = result.get("completedDefinitionEntries", [])

            embed = discord.Embed(
                title=f"<a:CS_decorate:1366286592758779995> Đã tìm được từ {result['completedWord']} <a:CS_decorate:1366286658260963450>",
                description=f"<a:CS_yeah:1463089379621998665> Người hoàn thành: {message.author.mention}",
            )

            if not definitionEntries:
                embed.add_field(
                    name="Giải thích",
                    value="Không có định nghĩa cho từ này.",
                    inline=False,
                )
            else:
                lines = []

                for index, entry in enumerate(definitionEntries, start=1):
                    partOfSpeech = entry.get("partOfSpeech") or "unknown"
                    definitionVi = entry.get("definitionVi") or entry.get("definitionEn") or ""
                    exampleEn = entry.get("exampleEn")
                    exampleVi = entry.get("exampleVi")

                    block = [
                        f"<a:CS_decorate:1366268034603417680> **Từ loại:** {partOfSpeech} \n"
                        f"<a:CS_decorate:1366268034603417680> **nghĩa:** {definitionVi}"
                    ]

                    if exampleEn:
                        block.append(f"*Example:* {exampleEn}")

                    if exampleVi:
                        block.append(f"*Dịch ví dụ:* {exampleVi}")

                    lines.append("\n".join(block))

                definitionText = "\n\n".join(lines)

                if len(definitionText) > 1000:
                    definitionText = definitionText[:997] + "..."

                embed.add_field(
                    name="**Giải thích**",
                    value=definitionText,
                    inline=False,
                )

            embed.set_footer(
                text=f"Từ mới đã được bắt đầu • Độ dài từ mới: {result['nextWordLength']} ký tự"
            )

            await message.channel.send(embed=embed)


async def setup(bot):
    await bot.add_cog(WordleEvent(bot))