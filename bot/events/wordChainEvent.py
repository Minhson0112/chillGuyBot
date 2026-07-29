import re
import unicodedata

import discord
from discord.ext import commands

from bot.config.channel import WORD_CHAIN_CHANNEL_ID
from bot.config.emoji import NO, PERFECT, YES
from bot.services.wordChain.wordChainGameService import WordChainGameService


class WordChainEvent(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.wordChainGameService = WordChainGameService()

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return

        if message.guild is None:
            return

        if message.channel.id != WORD_CHAIN_CHANNEL_ID:
            return

        phrase = self.normalizePhrase(message.content)

        if len(phrase.split(" ")) != 2:
            return

        result = await self.wordChainGameService.submitPhrase(
            bot=self.bot,
            phraseInput=phrase,
            userId=message.author.id,
        )

        if not result["success"]:
            await message.add_reaction(NO)

            if result.get("message") is not None:
                await message.channel.send(result["message"])

            return

        await message.add_reaction(YES)

        if result["isCompleted"]:
            await message.add_reaction(PERFECT)

    def normalizePhrase(self, value: str):
        value = unicodedata.normalize("NFC", value)
        value = value.strip().lower()
        value = re.sub(r"\s+", " ", value)

        return value


async def setup(bot):
    await bot.add_cog(WordChainEvent(bot))
