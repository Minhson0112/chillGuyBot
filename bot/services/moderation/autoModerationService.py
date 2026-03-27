from datetime import timedelta
import re

import discord

from bot.config.config import (
    AUTO_MUTE_DURATION_MINUTES,
    AUTO_MUTE_WARNING_THRESHOLD,
    BANNED_WORDS,
    MOD_COMMAND_CHANNEL_ID,
    MOD_ADMIN_USER_IDS,
)
from bot.config.database import getDbSession
from bot.enums.moderationActionType import ModerationActionType
from bot.repository.memberModerationHistoryRepository import MemberModerationHistoryRepository
from bot.repository.memberRepository import MemberRepository


class AutoModerationService:
    def __init__(self):
        self.bannedWordSet = {word.lower() for word in BANNED_WORDS}
        self.wordPattern = re.compile(r"\w+", flags=re.UNICODE)

    async def handleMessage(self, bot, message: discord.Message):
        if message.author.bot:
            return

        if message.guild is None:
            return

        if not isinstance(message.author, discord.Member):
            return

        if message.author.id in MOD_ADMIN_USER_IDS:
            return

        matchedWord = self.findMatchedBannedWord(message.content)

        if matchedWord is None:
            return

        with getDbSession() as session:
            memberRepository = MemberRepository(session)
            memberModerationHistoryRepository = MemberModerationHistoryRepository(session)

            member = memberRepository.findByUserId(message.author.id)
            if member is None:
                return

            member = memberRepository.incrementWarningCount(message.author.id)
            if member is None:
                return

            warningCount = member.warning_count
            modChannel = self.getModChannel(message.guild)

            if warningCount < AUTO_MUTE_WARNING_THRESHOLD:
                session.commit()

                if modChannel is not None:
                    await modChannel.send(
                        f"{message.author.mention}, bạn bị cảnh cáo lần {warningCount} vì dùng từ ngữ không phù hợp tại {message.jump_url}"
                    )
                return

            memberRepository.resetWarningCount(message.author.id)

            muteReason = f"warning lần {AUTO_MUTE_WARNING_THRESHOLD} và bị mute {AUTO_MUTE_DURATION_MINUTES} phút"
            until = discord.utils.utcnow() + timedelta(minutes=AUTO_MUTE_DURATION_MINUTES)
            await message.author.timeout(until, reason=muteReason)

            memberModerationHistoryRepository.create({
                "action_by_user_id": bot.user.id,
                "target_user_id": message.author.id,
                "action_type": ModerationActionType.MUTE.value,
                "reason": muteReason,
                "duration_minutes": AUTO_MUTE_DURATION_MINUTES,
            })

            session.commit()

            if modChannel is not None:
                embed = discord.Embed(
                    title="Member đã bị mute",
                    description="Hành động moderation đã được thực hiện thành công.",
                )
                embed.add_field(
                    name="Người mute",
                    value=f"{bot.user.mention}",
                    inline=False,
                )
                embed.add_field(
                    name="Người bị mute",
                    value=f"{message.author.mention}",
                    inline=False,
                )
                embed.add_field(
                    name="Thời lượng",
                    value=f"{AUTO_MUTE_DURATION_MINUTES} phút",
                    inline=False,
                )
                embed.add_field(
                    name="Lý do",
                    value=muteReason,
                    inline=False,
                )

                await modChannel.send(
                    content=f"{message.author.mention}, bạn bị cảnh cáo lần {AUTO_MUTE_WARNING_THRESHOLD} tại {message.jump_url}",
                    embed=embed,
                )

    def findMatchedBannedWord(self, content):
        normalizedContent = content.lower()
        tokens = self.wordPattern.findall(normalizedContent)

        for token in tokens:
            if token in self.bannedWordSet:
                return token

        return None

    def getModChannel(self, guild):
        return guild.get_channel(MOD_COMMAND_CHANNEL_ID)