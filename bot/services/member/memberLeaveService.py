from datetime import datetime, timezone

import discord

from bot.config.config import BYE_CHANNEL_ID, LOGO, MOD_COMMAND_CHANNEL_ID
from bot.config.database import getDbSession
from bot.repository.memberRepository import MemberRepository
from bot.repository.partnerRepository import PartnerRepository


class MemberLeaveService:
    async def handleMemberLeave(self, bot, discordMember: discord.Member):
        leaveAt = datetime.now(timezone.utc).replace(tzinfo=None)

        with getDbSession() as session:
            memberRepository = MemberRepository(session)
            partnerRepository = PartnerRepository(session)

            member = memberRepository.updateLeaveAt(discordMember.id, leaveAt)
            partnerGuildName = None

            if member is None:
                session.commit()
                return

            displayName = member.global_name or member.username
            joinedAt = member.joined_at
            leaveAtValue = member.leave_at
            isPartner = member.is_partner
            totalMsgCount = member.chat.total_chat_count if member.chat is not None else 0

            if isPartner:
                partner = partnerRepository.findByRepresentativeUserId(member.user_id)
                if partner is not None:
                    partnerGuildName = partner.guild_name

            session.commit()

        if joinedAt is None or leaveAtValue is None:
            stayDurationText = "một khoảng thời gian"
        else:
            stayDuration = leaveAtValue - joinedAt
            totalSeconds = int(stayDuration.total_seconds())
            totalMinutes = totalSeconds // 60

            days = totalMinutes // (24 * 60)
            remainingMinutes = totalMinutes % (24 * 60)
            hours = remainingMinutes // 60
            minutes = remainingMinutes % 60

            stayDurationText = f"{days} ngày {hours} giờ {minutes} phút"

        byeChannel = bot.get_channel(BYE_CHANNEL_ID)
        if byeChannel is None:
            try:
                byeChannel = await bot.fetch_channel(BYE_CHANNEL_ID)
            except discord.HTTPException:
                byeChannel = None

        if byeChannel is not None:
            await byeChannel.send(
                f"Hội ngộ rồi sẽ biệt ly. Tạm biệt **{displayName}** bạn đã ở trong Chill Station _{stayDurationText}_ và để lại **{totalMsgCount}** tin nhắn, hẹn gặp lại ở những chuyến tàu tới.🚉\n"
                f"# {LOGO}"
            )

        if isPartner and partnerGuildName is not None:
            modChannel = bot.get_channel(MOD_COMMAND_CHANNEL_ID)
            if modChannel is None:
                try:
                    modChannel = await bot.fetch_channel(MOD_COMMAND_CHANNEL_ID)
                except discord.HTTPException:
                    modChannel = None

            if modChannel is not None:
                await modChannel.send(
                    f"Người đại diện của server partner {partnerGuildName} đã rời Chill Station, hãy kiểm tra lại."
                )