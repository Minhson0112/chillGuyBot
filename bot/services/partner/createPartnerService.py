from datetime import date

import discord

from bot.config.config import PARTNER_CHANNEL_ID, PARTNER_ROLE_ID
from bot.config.database import getDbSession
from bot.repository.memberRepository import MemberRepository
from bot.repository.partnerRepository import PartnerRepository


class CreatePartnerService:
    async def createPartner(self, bot, interaction: discord.Interaction, inviteLink: str, representativeMember: discord.Member) -> str:
        try:
            invite = await bot.fetch_invite(inviteLink, with_counts=True)
        except discord.NotFound:
            return "Link mời không tồn tại hoặc đã hết hạn."
        except discord.HTTPException:
            return "Không thể lấy thông tin từ link mời."

        if invite.guild is None:
            return "Không lấy được thông tin guild từ link mời."

        guildId = invite.guild.id
        guildName = invite.guild.name
        representativeUserId = representativeMember.id
        partneredByUserId = interaction.user.id

        with getDbSession() as session:
            partnerRepository = PartnerRepository(session)
            memberRepository = MemberRepository(session)

            existedPartner = partnerRepository.findByGuildId(guildId)
            if existedPartner is not None:
                return f"Server {guildName} đã tồn tại trong danh sách partner."

            representativeDbMember = memberRepository.findByUserId(representativeUserId)
            if representativeDbMember is None:
                return "Người đại diện chưa tồn tại trong server."

            partnerRepository.create({
                "guild_id": guildId,
                "guild_name": guildName,
                "representative_user_id": representativeUserId,
                "partnered_by_user_id": partneredByUserId,
                "partner_at": date.today(),
            })

            memberRepository.updateIsPartner(representativeUserId, True)

            session.commit()

        role = interaction.guild.get_role(PARTNER_ROLE_ID) if interaction.guild is not None else None
        if role is None:
            role = bot.get_guild(interaction.guild.id).get_role(PARTNER_ROLE_ID) if interaction.guild is not None else None

        if role is None:
            return "Tạo partner thành công nhưng không tìm thấy role partner."

        await representativeMember.add_roles(role, reason=f"Create partner by {interaction.user.id}")

        partnerChannel = bot.get_channel(PARTNER_CHANNEL_ID)
        if partnerChannel is None:
            try:
                partnerChannel = await bot.fetch_channel(PARTNER_CHANNEL_ID)
            except discord.HTTPException:
                return "Tạo partner thành công nhưng không tìm thấy kênh thông báo partner."

        await partnerChannel.send(
            f"<a:CS_canhl:1357353968304652491> {guildName} <a:CS_canhr:1357353966341587107>\n"
            f"<a:CS_decorate:1366268034603417680> Người đại diện: {representativeMember.mention}\n"
            f"<a:CS_decorate:1366268034603417680> Người làm: {interaction.user.mention}"
        )

        return f"Đã tạo partner cho server {guildName} thành công."