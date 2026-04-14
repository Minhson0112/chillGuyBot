import re

import discord
from discord.ext import commands
from bot.config.emoji import LOGO
from bot.config.channel import DONATE_CHANNEL_ID
from bot.config.userId import OWO_BOT_ID, TREASURER_MEMBER_ID_LIST
from bot.services.donate.donateRewardService import DonateRewardService


class OwoDonateEvent(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.donateRewardService = DonateRewardService()
        self.processedMessageIds = set()

    @commands.Cog.listener()
    async def on_message_edit(self, before: discord.Message, after: discord.Message):
        if before.content == after.content:
            return

        await self.handleDonateMessage(after)

    async def handleDonateMessage(self, message: discord.Message):
        if message.guild is None:
            return

        if message.author.id != OWO_BOT_ID:
            return

        if message.channel.id != DONATE_CHANNEL_ID:
            return

        if message.id in self.processedMessageIds:
            return

        donateInfo = self.extractDonateInfo(message.content)
        if donateInfo is None:
            return

        senderUserId = donateInfo["senderUserId"]
        receiverUserId = donateInfo["receiverUserId"]
        donatedCowoncy = donateInfo["donatedCowoncy"]

        if receiverUserId not in TREASURER_MEMBER_ID_LIST:
            return

        senderMember = message.guild.get_member(senderUserId)
        if senderMember is None:
            try:
                senderMember = await message.guild.fetch_member(senderUserId)
            except discord.NotFound:
                return
            except discord.HTTPException:
                return

        receiverMember = message.guild.get_member(receiverUserId)
        if receiverMember is None:
            try:
                receiverMember = await message.guild.fetch_member(receiverUserId)
            except discord.NotFound:
                return
            except discord.HTTPException:
                return

        await self.donateRewardService.processDonateReward(
            guild=message.guild,
            senderMember=senderMember,
            receiverMember=receiverMember,
            cowoncyAmount=donatedCowoncy,
        )

        self.processedMessageIds.add(message.id)

        await message.channel.send(
            self.buildThankYouMessage(
                senderMember=senderMember,
                donatedCowoncy=donatedCowoncy,
            )
        )

    def extractDonateInfo(self, content: str):
        normalizedContent = content.strip()

        match = re.search(
            r"\**💳\s*\|\s*<@!?(\d+)>\**\s*sent\s*\**([\d,]+)\s+cowoncy\**\s*to\s*\**<@!?(\d+)>\**!",
            normalizedContent,
            re.IGNORECASE,
        )
        if match is None:
            return None

        senderUserId = int(match.group(1))
        donatedCowoncy = int(match.group(2).replace(",", ""))
        receiverUserId = int(match.group(3))

        return {
            "senderUserId": senderUserId,
            "receiverUserId": receiverUserId,
            "donatedCowoncy": donatedCowoncy,
        }

    def buildThankYouMessage(self, senderMember: discord.Member, donatedCowoncy: int):
        return (
            "# <a:CS_decorate:1366286592758779995> Cảm Ơn Donate <a:CS_decorate:1366286658260963450>\n"
            f"Thay mặt {LOGO} cảm ơn {senderMember.mention} rất nhiều <a:CS_tim1:1466240640089325588>, "
            f"chúng tớ đã nhận được {donatedCowoncy:,} cowoncy, chúc bạn một ngày tốt lành."
        )


async def setup(bot):
    await bot.add_cog(OwoDonateEvent(bot))