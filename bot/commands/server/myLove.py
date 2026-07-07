import discord
from discord.ext import commands

from bot.services.serverItem.coupleProfileService import CoupleProfileService


class MyLoveCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.coupleProfileService = CoupleProfileService()

    @commands.command(name="mylove")
    async def myLove(self, ctx: commands.Context):
        if ctx.guild is None:
            return

        result = self.coupleProfileService.getCoupleProfile(ctx.author.id)

        if not result["success"]:
            await ctx.reply(
                result["message"],
                mention_author=False,
            )
            return

        coupleProfile = result["couple"]
        user1 = await self.getGuildMember(ctx.guild, coupleProfile["user1Id"])
        user2 = await self.getGuildMember(ctx.guild, coupleProfile["user2Id"])

        if user1 is None or user2 is None:
            await ctx.reply(
                "Không tìm thấy đủ thông tin member của couple trong server.",
                mention_author=False,
            )
            return

        imageBuffer = await self.coupleProfileService.buildCoupleProfileImage(
            user1=user1,
            user2=user2,
            coupleProfile=coupleProfile,
        )
        file = discord.File(imageBuffer, filename="mylove.png")

        await ctx.reply(
            file=file,
            mention_author=False,
        )

    async def getGuildMember(self, guild, userId: int):
        member = guild.get_member(userId)

        if member is not None:
            return member

        try:
            return await guild.fetch_member(userId)
        except (discord.NotFound, discord.HTTPException):
            return None


async def setup(bot):
    await bot.add_cog(MyLoveCommand(bot))
