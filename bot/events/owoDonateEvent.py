import re

import discord
from discord.ext import commands

from bot.config.config import (
    DONATE_CHANNEL_ID,
    LOGO,
    OWO_BOT_ID,
    TREASURER_MEMBER_ID_LIST,
)
from bot.services.donate.donateRewardService import DonateRewardService


class OwoDonateEvent(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.donateRewardService = DonateRewardService()

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.guild is None:
            return

        if message.author.id != OWO_BOT_ID:
            return

        if message.channel.id != DONATE_CHANNEL_ID:
            return

        if not self.isOwoDonateMessage(message):
            return

        senderMember, receiverMember = self.getSenderAndReceiver(message)
        if senderMember is None or receiverMember is None:
            return

        if receiverMember.id not in TREASURER_MEMBER_ID_LIST:
            return

        donatedCowoncy = self.extractCowoncyAmount(message.content)
        if donatedCowoncy is None:
            return

        await self.donateRewardService.processDonateReward(
            guild=message.guild,
            senderMember=senderMember,
            receiverMember=receiverMember,
            cowoncyAmount=donatedCowoncy,
        )

        await message.channel.send(
            self.buildThankYouMessage(
                senderMember=senderMember,
                donatedCowoncy=donatedCowoncy,
            )
        )

    def isOwoDonateMessage(self, message: discord.Message):
        if len(message.mentions) < 2:
            return False

        content = message.content.lower()

        if " sent " not in content:
            return False

        if " cowoncy to " not in content:
            return False

        return True

    def getSenderAndReceiver(self, message: discord.Message):
        if len(message.mentions) < 2:
            return None, None

        senderMember = message.mentions[0]
        receiverMember = message.mentions[1]

        return senderMember, receiverMember

    def extractCowoncyAmount(self, content: str):
        match = re.search(r"sent\s+([\d,]+)\s+cowoncy\s+to", content, re.IGNORECASE)
        if match is None:
            return None

        return int(match.group(1).replace(",", ""))

    def buildThankYouMessage(self, senderMember: discord.Member, donatedCowoncy: int):
        return (
            "# <a:CS_decorate:1366286592758779995> Cảm Ơn Donate <a:CS_decorate:1366286658260963450>\n"
            f"Thay mặt {LOGO} cảm ơn {senderMember.mention} rất nhiều <a:CS_tim1:1466240640089325588>, "
            f"chúng tớ đã nhận được {donatedCowoncy:,} cowoncy, chúc bạn một ngày tốt lành."
        )


async def setup(bot):
    await bot.add_cog(OwoDonateEvent(bot))