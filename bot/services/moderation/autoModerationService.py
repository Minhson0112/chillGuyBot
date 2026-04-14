from datetime import timedelta
import re
import unicodedata

import discord

from bot.config.config import (
    AUTO_MUTE_DURATION_MINUTES,
    AUTO_MUTE_WARNING_THRESHOLD,
    BANNED_WORDS,
)
from bot.config.channel import MOD_COMMAND_CHANNEL_ID
from bot.config.roles import OWNER_ROLE_ID
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

        if self.hasOwnerRole(message.author):
            return

        if await self.handleEveryoneMention(bot, message):
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

    async def handleEveryoneMention(self, bot, message: discord.Message):
        if not self.isEveryoneMentionViolation(message):
            return False

        with getDbSession() as session:
            memberRepository = MemberRepository(session)
            memberModerationHistoryRepository = MemberModerationHistoryRepository(session)

            member = memberRepository.findByUserId(message.author.id)
            if member is None:
                return False

            banReason = "người dùng đã tag everyone hoặc here (chống raid server)"

            try:
                await message.delete()
            except discord.Forbidden:
                pass
            except discord.NotFound:
                pass

            await message.author.ban(reason=banReason, delete_message_days=1)

            memberModerationHistoryRepository.create({
                "action_by_user_id": bot.user.id,
                "target_user_id": message.author.id,
                "action_type": ModerationActionType.BAN.value,
                "reason": banReason,
                "duration_minutes": None,
            })

            session.commit()

            modChannel = self.getModChannel(message.guild)
            if modChannel is not None:
                embed = discord.Embed(
                    title="Member đã bị ban",
                    description="Hành động moderation đã được thực hiện thành công.",
                )
                embed.add_field(
                    name="Người ban",
                    value=f"{bot.user.mention}",
                    inline=False,
                )
                embed.add_field(
                    name="Người bị ban",
                    value=f"{message.author.mention}",
                    inline=False,
                )
                embed.add_field(
                    name="Lý do",
                    value=banReason,
                    inline=False,
                )
                embed.add_field(
                    name="Tin nhắn",
                    value=message.jump_url,
                    inline=False,
                )

                await modChannel.send(embed=embed)

        return True

    def isEveryoneMentionViolation(self, message: discord.Message):
        if message.mention_everyone:
            return True

        normalizedContent = self.normalizeMentionContent(message.content)

        if "@everyone" in normalizedContent:
            return True

        if "@here" in normalizedContent:
            return True

        return False

    def normalizeMentionContent(self, content: str):
        normalized = unicodedata.normalize("NFKC", content).lower()

        filteredChars = []
        for char in normalized:
            if unicodedata.category(char) == "Cf":
                continue
            filteredChars.append(char)

        return "".join(filteredChars)

    def hasOwnerRole(self, member: discord.Member):
        return any(role.id == OWNER_ROLE_ID for role in member.roles)

    def findMatchedBannedWord(self, content):
        normalizedContent = content.lower()
        tokens = self.wordPattern.findall(normalizedContent)

        for token in tokens:
            if token in self.bannedWordSet:
                return token

        return None

    def getModChannel(self, guild):
        return guild.get_channel(MOD_COMMAND_CHANNEL_ID)