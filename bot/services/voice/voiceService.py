import io

import discord


class VoiceService:
    async def joinAuthorChannel(self, ctx):
        if ctx.guild is None:
            await ctx.send("Lệnh này chỉ dùng được trong server.")
            return None

        if ctx.author.voice is None or ctx.author.voice.channel is None:
            await ctx.send("Bạn cần vào voice channel trước.")
            return None

        targetChannel = ctx.author.voice.channel
        voiceClient = ctx.guild.voice_client

        if voiceClient is None:
            return await targetChannel.connect()

        if voiceClient.channel.id != targetChannel.id:
            await voiceClient.move_to(targetChannel)

        return voiceClient

    async def leave(self, ctx):
        if ctx.guild is None:
            await ctx.send("Lệnh này chỉ dùng được trong server.")
            return

        voiceClient = ctx.guild.voice_client
        if voiceClient is None:
            await ctx.send("Bot hiện không ở trong voice channel.")
            return

        await voiceClient.disconnect()
        await ctx.send("Bot đã rời voice channel.")

    async def playBuffer(self, ctx, audioBuffer: io.BytesIO):
        if ctx.guild is None:
            audioBuffer.close()
            await ctx.send("Lệnh này chỉ dùng được trong server.")
            return

        voiceClient = ctx.guild.voice_client
        if voiceClient is None:
            voiceClient = await self.joinAuthorChannel(ctx)
            if voiceClient is None:
                audioBuffer.close()
                return

        if ctx.author.voice is None or ctx.author.voice.channel is None:
            audioBuffer.close()
            await ctx.send("Bạn cần vào voice channel trước.")
            return

        if voiceClient.channel.id != ctx.author.voice.channel.id:
            audioBuffer.close()
            await ctx.send("Bạn cần ở cùng voice channel với bot.")
            return

        if voiceClient.is_playing():
            audioBuffer.close()
            await ctx.send("Bot đang phát âm thanh khác.")
            return

        source = discord.FFmpegPCMAudio(
            audioBuffer,
            pipe=True,
            before_options="-loglevel error",
        )

        def afterPlay(error):
            try:
                audioBuffer.close()
            except Exception:
                pass

            if error:
                print(f"Voice play error: {error}")

        voiceClient.play(source, after=afterPlay)