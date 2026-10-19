import traceback

from discord.ext import commands

from bot.services.voice.textToSpeechService import TextToSpeechService
from bot.services.voice.voiceService import VoiceService


class Speak(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.textToSpeechService = TextToSpeechService()
        self.voiceService = VoiceService()

    @commands.command(name="s")
    async def speak(self, ctx, *, text: str):
        print(f"[cg s] Received: messageId={ctx.message.id}, userId={ctx.author.id}", flush=True)
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

        try:
            audioBuffer = await self.textToSpeechService.synthesize(text)
            print(f"[cg s] Starting voice playback: messageId={ctx.message.id}", flush=True)
            await self.voiceService.playBuffer(ctx, audioBuffer)
        except Exception:
            print(f"[cg s] Failed: messageId={ctx.message.id}", flush=True)
            traceback.print_exc()
            raise


async def setup(bot):
    await bot.add_cog(Speak(bot))
