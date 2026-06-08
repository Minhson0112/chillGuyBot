import re

import discord
from discord.ext import commands

from bot.config.channel import DONATE_CHANNEL_ID, EXCHANGE_COIN_CHANNEL_ID, PAYMENT_CHANNEL_ID
from bot.config.userId import OWO_BOT_ID
from bot.services.owo.owoGiveChannelService import OwoGiveChannelService


class OwoGiveEvent(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.owoGiveChannelService = OwoGiveChannelService()
        self.processedMessageIds = set()

    @commands.Cog.listener()
    async def on_message_edit(self, before: discord.Message, after: discord.Message):
        if before.content == after.content:
            return

        await self.handleOwoGiveMessage(after)

    async def handleOwoGiveMessage(self, message: discord.Message):
        if message.guild is None:
            return

        if message.author.id != OWO_BOT_ID:
            return

        if message.channel.id not in [
            DONATE_CHANNEL_ID,
            EXCHANGE_COIN_CHANNEL_ID,
            PAYMENT_CHANNEL_ID,
        ]:
            return

        if message.id in self.processedMessageIds:
            return

        giveInfo = self.extractOwoGiveInfo(message.content)

        if giveInfo is None:
            return

        senderUserId = giveInfo["senderUserId"]
        receiverUserId = giveInfo["receiverUserId"]
        cowoncyAmount = giveInfo["cowoncyAmount"]

        if message.channel.id == DONATE_CHANNEL_ID:
            isProcessed = await self.owoGiveChannelService.handleDonateChannel(
                message=message,
                senderUserId=senderUserId,
                receiverUserId=receiverUserId,
                cowoncyAmount=cowoncyAmount,
            )
            self.markProcessedMessage(message.id, isProcessed)
            return

        if message.channel.id == EXCHANGE_COIN_CHANNEL_ID:
            isProcessed = await self.owoGiveChannelService.handleExchangeCoinChannel(
                message=message,
                senderUserId=senderUserId,
                receiverUserId=receiverUserId,
                cowoncyAmount=cowoncyAmount,
            )
            self.markProcessedMessage(message.id, isProcessed)
            return

        if message.channel.id == PAYMENT_CHANNEL_ID:
            isProcessed = await self.owoGiveChannelService.handlePaymentChannel(
                message=message,
                senderUserId=senderUserId,
                receiverUserId=receiverUserId,
                cowoncyAmount=cowoncyAmount,
            )
            self.markProcessedMessage(message.id, isProcessed)
            return

    def markProcessedMessage(self, messageId: int, isProcessed: bool):
        if isProcessed:
            self.processedMessageIds.add(messageId)

    def extractOwoGiveInfo(self, content: str):
        normalizedContent = content.strip()

        match = re.search(
            r"\**💳\s*\|\s*<@!?(\d+)>\**\s*sent\s*\**([\d,]+)\s+cowoncy\**\s*to\s*\**<@!?(\d+)>\**!",
            normalizedContent,
            re.IGNORECASE,
        )

        if match is None:
            return None

        senderUserId = int(match.group(1))
        cowoncyAmount = int(match.group(2).replace(",", ""))
        receiverUserId = int(match.group(3))

        return {
            "senderUserId": senderUserId,
            "receiverUserId": receiverUserId,
            "cowoncyAmount": cowoncyAmount,
        }

async def setup(bot):
    await bot.add_cog(OwoGiveEvent(bot))
