from discord.ext import commands

from bot.services.voice.textToSpeechService import TextToSpeechService
from bot.services.voice.voiceService import VoiceService


class Speak(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.textToSpeechService = TextToSpeechService()
        self.voiceService = VoiceService()

    @commands.command(name="speak")
    async def speak(self, ctx, *, text: str):
        if ctx.guild is None:
            await ctx.send("Lệnh này chỉ dùng được trong server.")
            return

        text = text.strip()
        if not text:
            await ctx.send("Bạn cần nhập nội dung để bot đọc.")
            return

        if len(text) > 300:
            await ctx.send("Nội dung quá dài. Hãy giữ dưới 300 ký tự.")
            return

        audioBuffer = await self.textToSpeechService.synthesize(text)
        await self.voiceService.playBuffer(ctx, audioBuffer)


async def setup(bot):
    await bot.add_cog(Speak(bot))