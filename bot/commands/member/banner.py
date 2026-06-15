import discord
from discord.ext import commands


class Banner(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="bn")
    async def banner(self, ctx, member: discord.Member = None):
        if member is None:
            member = ctx.author

        user = await self.bot.fetch_user(member.id)

        if user.banner is None:
            await ctx.send(f"{member.display_name} không có banner.")
            return

        embed = discord.Embed(title=f"Banner của {member.display_name}")
        embed.set_image(url=user.banner.url)

        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Banner(bot))
