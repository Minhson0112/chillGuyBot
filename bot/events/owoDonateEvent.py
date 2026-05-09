import re

import discord
from discord.ext import commands

from bot.config.channel import DONATE_CHANNEL_ID, EXCHANGE_COIN_CHANNEL_ID
from bot.config.emoji import LOGO
from bot.config.userId import OWNER_ID, OWO_BOT_ID, TREASURER_MEMBER_ID_LIST
from bot.services.donate.donateRewardService import DonateRewardService
from bot.services.exchange.owoExchangeCoinService import OwoExchangeCoinService


class OwoGiveEvent(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.donateRewardService = DonateRewardService()
        self.owoExchangeCoinService = OwoExchangeCoinService()
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
            await self.handleDonateChannel(
                message=message,
                senderUserId=senderUserId,
                receiverUserId=receiverUserId,
                cowoncyAmount=cowoncyAmount,
            )
            return

        if message.channel.id == EXCHANGE_COIN_CHANNEL_ID:
            await self.handleExchangeCoinChannel(
                message=message,
                senderUserId=senderUserId,
                receiverUserId=receiverUserId,
                cowoncyAmount=cowoncyAmount,
            )
            return

    async def handleDonateChannel(
        self,
        message: discord.Message,
        senderUserId: int,
        receiverUserId: int,
        cowoncyAmount: int,
    ):
        if receiverUserId not in TREASURER_MEMBER_ID_LIST:
            return

        senderMember = await self.resolveGuildMember(
            guild=message.guild,
            userId=senderUserId,
        )

        if senderMember is None:
            return

        receiverMember = await self.resolveGuildMember(
            guild=message.guild,
            userId=receiverUserId,
        )

        if receiverMember is None:
            return

        await self.donateRewardService.processDonateReward(
            guild=message.guild,
            senderMember=senderMember,
            receiverMember=receiverMember,
            cowoncyAmount=cowoncyAmount,
        )

        self.processedMessageIds.add(message.id)

        await message.channel.send(
            self.buildThankYouMessage(
                senderMember=senderMember,
                donatedCowoncy=cowoncyAmount,
            )
        )

    async def handleExchangeCoinChannel(
        self,
        message: discord.Message,
        senderUserId: int,
        receiverUserId: int,
        cowoncyAmount: int,
    ):
        if receiverUserId != OWNER_ID:
            return

        senderMember = await self.resolveGuildMember(
            guild=message.guild,
            userId=senderUserId,
        )

        if senderMember is None:
            return

        receiverMember = await self.resolveGuildMember(
            guild=message.guild,
            userId=receiverUserId,
        )

        if receiverMember is None:
            return

        exchangeResult = self.owoExchangeCoinService.exchangeCoin(
            messageId=message.id,
            channelId=message.channel.id,
            senderUserId=senderUserId,
            receiverUserId=receiverUserId,
            cowoncyAmount=cowoncyAmount,
        )

        if not exchangeResult["success"]:
            await message.channel.send(exchangeResult["message"])
            return

        self.processedMessageIds.add(message.id)

        await message.channel.send(
            self.buildExchangeCoinMessage(
                senderMember=senderMember,
                cowoncyAmount=cowoncyAmount,
                chillCoinAmount=exchangeResult["chillCoinAmount"],
            )
        )

    async def resolveGuildMember(
        self,
        guild: discord.Guild,
        userId: int,
    ):
        guildMember = guild.get_member(userId)

        if guildMember is not None:
            return guildMember

        try:
            return await guild.fetch_member(userId)
        except discord.NotFound:
            return None
        except discord.HTTPException:
            return None

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

    def buildThankYouMessage(
        self,
        senderMember: discord.Member,
        donatedCowoncy: int,
    ):
        return (
            "# <a:CS_decorate:1366286592758779995> Cảm Ơn Donate <a:CS_decorate:1366286658260963450>\n"
            f"Thay mặt {LOGO} cảm ơn {senderMember.mention} rất nhiều <a:CS_tim1:1466240640089325588>, "
            f"chúng tớ đã nhận được {donatedCowoncy:,} cowoncy, chúc bạn một ngày tốt lành."
        )

    def buildExchangeCoinMessage(
        self,
        senderMember: discord.Member,
        cowoncyAmount: int,
        chillCoinAmount: int,
    ):
        return (
            f"{senderMember.mention} đã chuyển **{cowoncyAmount:,}** cowoncy thành công.\n"
            f"Bạn nhận được **{chillCoinAmount:,}** <:cs_coin:1495116560191324383>."
        )


async def setup(bot):
    await bot.add_cog(OwoGiveEvent(bot))