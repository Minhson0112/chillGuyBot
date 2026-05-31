from discord.ext import commands

from bot.services.anonymousMatch.anonymousMatchService import AnonymousMatchService


class AnonymousMatchCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.anonymousMatchService = AnonymousMatchService()

    @commands.command(name="match")
    async def match(self, ctx: commands.Context):
        result = await self.anonymousMatchService.registerMatch(self.bot, ctx.author)

        if not result["success"]:
            await ctx.reply(result["message"], mention_author=False)
            return

        if not result["matched"]:
            await ctx.reply(result["message"], mention_author=False)
            return

        isDmSent = await self.anonymousMatchService.sendMatchedMessages(self.bot, result)
        if isDmSent:
            await ctx.reply("Đã ghép đôi thành công, hãy kiểm tra DM của bạn.", mention_author=False)
            return

        await ctx.reply(
            "Đã ghép đôi thành công nhưng tôi không gửi được DM cho ít nhất một người.",
            mention_author=False,
        )


async def setup(bot):
    await bot.add_cog(AnonymousMatchCommand(bot))
