import discord
from discord.ext import commands


class Avatar(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="av")
    async def avatar(self, ctx, member: discord.Member = None):
        if member is None:
            member = ctx.author

        embed = discord.Embed(
            title=f"Avatar của {member.display_name}"
        )
        embed.set_image(url=member.display_avatar.url)

        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Avatar(bot))