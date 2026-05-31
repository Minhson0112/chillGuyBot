from discord.ext import commands

from bot.services.anonymousMatch.anonymousMatchStopService import AnonymousMatchStopService


class AnonymousMatchStopCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.anonymousMatchStopService = AnonymousMatchStopService()

    @commands.command(name="stop")
    async def stop(self, ctx: commands.Context):
        if ctx.guild is not None:
            await ctx.reply("Lệnh này chỉ dùng được trong DM với bot.", mention_author=False)
            return

        result = await self.anonymousMatchStopService.stopMatch(self.bot, ctx.author)
        await ctx.reply(result["message"], mention_author=False)

        if not result["success"]:
            return

        if result["ended"]:
            await self.anonymousMatchStopService.notifyPartnerEnded(
                self.bot,
                result["partnerUserId"],
            )


async def setup(bot):
    await bot.add_cog(AnonymousMatchStopCommand(bot))
