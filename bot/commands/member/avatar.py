import discord
from discord.ext import commands

from bot.views.avatarView import AvatarView


class Avatar(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="av")
    async def avatar(self, ctx, member: discord.Member = None):
        if member is None:
            member = ctx.author

        view = AvatarView(member)

        await ctx.send(
            embed=view.buildAvatarEmbed("server"),
            view=view,
        )


async def setup(bot):
    await bot.add_cog(Avatar(bot))
