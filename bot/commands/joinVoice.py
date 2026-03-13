from discord.ext import commands

class JoinVoice(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="join")
    async def join(self, ctx):
        if ctx.guild is None:
            await ctx.send("Lệnh này chỉ dùng được trong server.")
            return

        if ctx.author.voice is None or ctx.author.voice.channel is None:
            await ctx.send("Bạn cần vào voice channel trước.")
            return

        targetChannel = ctx.author.voice.channel
        voiceClient = ctx.guild.voice_client

        if voiceClient is None:
            await targetChannel.connect()
            await ctx.send(f"Đã vào voice channel: {targetChannel.name}")
            return

        if voiceClient.channel.id == targetChannel.id:
            await ctx.send("Bot đã ở sẵn trong voice channel của bạn rồi.")
            return

        await voiceClient.move_to(targetChannel)
        await ctx.send(f"Đã chuyển sang voice channel: {targetChannel.name}")


async def setup(bot):
    await bot.add_cog(JoinVoice(bot))
