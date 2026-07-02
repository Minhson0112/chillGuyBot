import discord
from discord.ext import commands

from bot.services.server.serverInfoImageService import ServerInfoImageService
from bot.services.server.serverInfoService import ServerInfoService


class ServerInfo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.serverInfoService = ServerInfoService()
        self.serverInfoImageService = ServerInfoImageService()

    @commands.command(name="serverinfo")
    async def serverInfo(self, ctx):
        if ctx.guild is None:
            await ctx.send("Lệnh này chỉ dùng được trong server.")
            return

        async with ctx.typing():
            serverInfo = self.serverInfoService.getServerInfo(ctx.guild)
            imageBuffer = await self.serverInfoImageService.buildServerInfoImage(
                ctx.guild,
                serverInfo,
            )

        file = discord.File(
            fp=imageBuffer,
            filename="server_info.png",
        )
        await ctx.send(file=file)


async def setup(bot):
    await bot.add_cog(ServerInfo(bot))
