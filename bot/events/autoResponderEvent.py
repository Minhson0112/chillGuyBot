import discord
from discord.ext import commands

from bot.services.autoResponder.autoResponderMatchService import AutoResponderMatchService


class AutoResponderEvent(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.autoResponderMatchService = AutoResponderMatchService()

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return

        if message.guild is None:
            return

        matchedKey = self.autoResponderMatchService.findMatchedKey(message.content)
        if matchedKey is None:
            return

        autoResponder = self.autoResponderMatchService.findAutoResponderByMatchedKey(matchedKey)
        if autoResponder is None:
            return

        if not self.autoResponderMatchService.canUseAutoResponder(autoResponder, message.author.id):
            return

        templateMessage = await self.autoResponderMatchService.fetchTemplateMessage(
            self.bot,
            autoResponder.msg_link
        )

        if templateMessage.content:
            await message.channel.send(templateMessage.content)

        for attachment in templateMessage.attachments:
            await message.channel.send(attachment.url)

async def setup(bot):
    await bot.add_cog(AutoResponderEvent(bot))