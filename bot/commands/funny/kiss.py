import random

import discord
from discord.ext import commands

from bot.config.gif import KISS


KISS_MESSAGES = [
    "{author} đã hôn {target} đắm đuối đến mức cả server phải quay mặt đi.",
    "{author} vừa trao cho {target} một nụ hôn ngọt hơn cả trà sữa full topping.",
    "{author} bất ngờ kéo {target} lại gần và hôn một cái nhẹ nhàng.",
    "{author} đã đặt lên môi {target} một nụ hôn khiến thời gian ngừng trôi.",
    "{author} vừa hôn {target} tới mức hai người quên luôn mình đang ở Discord.",
    "{author} gửi tặng {target} một nụ hôn nóng hơn mặt trời.",
    "{author} đã hôn {target} một cách đầy cảm xúc.",
    "{author} vừa khóa môi {target}, hội độc thân trong server đồng loạt tổn thương.",
]


class KissCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="kiss")
    async def kiss(
        self,
        ctx: commands.Context,
        member: discord.Member = None,
    ):
        if member is None:
            await ctx.reply(
                "Cách dùng: `cg kiss @user`",
                mention_author=False,
            )
            return

        message = random.choice(KISS_MESSAGES).format(
            author=ctx.author.mention,
            target=member.mention,
        )
        embed = discord.Embed(
            description=message,
            color=discord.Color.magenta(),
        )
        embed.set_image(url=random.choice(KISS))

        await ctx.reply(
            embed=embed,
            mention_author=False,
        )


async def setup(bot):
    await bot.add_cog(KissCommand(bot))
