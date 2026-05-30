import discord
from discord.ext import commands

from bot.config.channel import MAIN_CHAT_CHANNEL_ID
from bot.config.userId import OWNER_ID


class ChatCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="chat")
    async def chat(self, ctx: commands.Context, *, message: str = None):
        if ctx.author.id != OWNER_ID:
            return

        if message is None:
            return

        mainChatChannel = (
            ctx.guild.get_channel(MAIN_CHAT_CHANNEL_ID)
            if ctx.guild is not None
            else None
        )
        if mainChatChannel is None:
            try:
                mainChatChannel = await self.bot.fetch_channel(MAIN_CHAT_CHANNEL_ID)
            except discord.HTTPException:
                return

        if not isinstance(mainChatChannel, discord.TextChannel):
            return

        await mainChatChannel.send(message)


async def setup(bot):
    await bot.add_cog(ChatCommand(bot))
