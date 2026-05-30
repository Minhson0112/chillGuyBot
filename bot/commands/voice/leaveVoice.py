from discord.ext import commands

class LeaveVoice(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="leave")
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


async def setup(bot):
    await bot.add_cog(LeaveVoice(bot))
