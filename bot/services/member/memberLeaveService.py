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
            partner = None

            if member is not None and member.is_partner:
                partner = partnerRepository.findByRepresentativeUserId(member.user_id)

            session.commit()

        if member is None:
            return

        displayName = member.global_name or member.username
        stayDuration = member.leave_at - member.joined_at

        byeChannel = bot.get_channel(BYE_CHANNEL_ID)
        if byeChannel is None:
            try:
                byeChannel = await bot.fetch_channel(BYE_CHANNEL_ID)
            except discord.HTTPException:
                byeChannel = None

        if byeChannel is not None:
            await byeChannel.send(
                f"Hội ngộ rồi sẽ biệt ly. Tạm biệt {displayName} bạn đã ở trong Chill Station {stayDuration} thời gian, hẹn gặp lại ở những chuyến tàu tới.🚉\n"
                f"# {LOGO}"
            )

        if member.is_partner and partner is not None:
            modChannel = bot.get_channel(MOD_COMMAND_CHANNEL_ID)
            if modChannel is None:
                try:
                    modChannel = await bot.fetch_channel(MOD_COMMAND_CHANNEL_ID)
                except discord.HTTPException:
                    modChannel = None

            if modChannel is not None:
                await modChannel.send(
                    f"Người đại diện của server {partner.guild_name} đã rời server, hãy kiểm tra lại."
                )