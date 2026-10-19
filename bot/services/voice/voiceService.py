import io
import traceback

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
            print(f"[Voice] Connecting: channelId={targetChannel.id}", flush=True)
            voiceClient = await targetChannel.connect()
            print(f"[Voice] Connected: channelId={targetChannel.id}", flush=True)
            return voiceClient

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
        print(f"[Voice] Playback requested: messageId={ctx.message.id}", flush=True)
        if ctx.guild is None:
            print("[Voice] Skipped: no guild", flush=True)
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
            print("[Voice] Skipped: author is not in voice", flush=True)
            await ctx.send("Bạn cần vào voice channel trước.")
            return

        if voiceClient.channel.id != ctx.author.voice.channel.id:
            audioBuffer.close()
            print("[Voice] Skipped: author is in another voice channel", flush=True)
            await ctx.send("Bạn cần ở cùng voice channel với bot.")
            return

        if voiceClient.is_playing():
            audioBuffer.close()
            print("[Voice] Skipped: already playing audio", flush=True)
            await ctx.send("Bot đang phát âm thanh khác.")
            return

        print(f"[Voice] Creating FFmpeg audio source: connected={voiceClient.is_connected()}", flush=True)
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
                print(f"[Voice] Playback failed: messageId={ctx.message.id}, error={error!r}", flush=True)
                traceback.print_exception(type(error), error, error.__traceback__)
            else:
                print(f"[Voice] Playback finished: messageId={ctx.message.id}", flush=True)

        voiceClient.play(source, after=afterPlay)
        print(f"[Voice] Playback started: messageId={ctx.message.id}", flush=True)
