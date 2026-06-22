import discord
from discord.ext import commands

from bot.views.member.bannerView import BannerView


class Banner(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="bn")
    async def banner(self, ctx, member: discord.Member = None):
        if member is None:
            member = ctx.author

        if ctx.guild is not None:
            try:
                member = await ctx.guild.fetch_member(member.id)
            except discord.DiscordException:
                pass

        user = await self.bot.fetch_user(member.id)
        view = BannerView(member, user.banner)

        await ctx.send(
            embed=view.buildBannerEmbed("server"),
            view=view,
        )


async def setup(bot):
    await bot.add_cog(Banner(bot))
