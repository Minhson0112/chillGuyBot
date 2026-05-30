from discord.ext import commands

from bot.services.server.serverInfoService import ServerInfoService


class ServerInfo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.serverInfoService = ServerInfoService()

    @commands.command(name="serverinfo")
    async def serverInfo(self, ctx):
        if ctx.guild is None:
            await ctx.send("Lệnh này chỉ dùng được trong server.")
            return

        embed = self.serverInfoService.buildServerInfoEmbed(ctx.guild)
        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(ServerInfo(bot))