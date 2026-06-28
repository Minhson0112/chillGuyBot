import discord
from discord.ext import commands

from bot.config.channel import BOOSTERS_CHANNEL_ID
from bot.config.emoji import BOOSTER, BOW_THANK_YOU, GIFT


class BoosterMessageEvent(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.guild is None:
            return

        if message.channel.id != BOOSTERS_CHANNEL_ID:
            return

        if message.type != discord.MessageType.premium_guild_subscription:
            return

        await message.channel.send(
            f"# {BOW_THANK_YOU} Cảm Ơn Booster {BOW_THANK_YOU}\n"
            f"{BOOSTER} Thay mặt Chill Station cảm ơn {message.author.mention} rất nhiều, "
            "chúc bạn 1 ngày tốt lành\n"
            f"{GIFT} Đừng quên lấy đặc quyền của booster nhé, tham khảo tại "
            "https://discord.com/channels/1356994231918530690/1502996579366338620/1516010158801682542"
        )


async def setup(bot):
    await bot.add_cog(BoosterMessageEvent(bot))
