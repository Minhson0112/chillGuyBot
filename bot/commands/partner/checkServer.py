from discord.ext import commands

from bot.services.partner.checkServerService import CheckServerService


class CheckServerCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.checkServerService = CheckServerService()

    @commands.command(name="checkserver")
    async def checkServer(self, ctx, inviteLink: str):
        result = await self.checkServerService.checkServer(self.bot, inviteLink)
        await ctx.send(result)

async def setup(bot):
    await bot.add_cog(CheckServerCommand(bot))
