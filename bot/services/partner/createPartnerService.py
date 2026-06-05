from datetime import date

import discord

from bot.config.channel import PARTNER_CHANNEL_ID
from bot.config.database import getDbSession
from bot.config.roles import PARTNER_ROLE_ID
from bot.enums.partnerStatus import PartnerStatus
from bot.repository.memberRepository import MemberRepository
from bot.repository.partnerRepository import PartnerRepository


class CreatePartnerService:
    async def createPartner(
        self,
        bot,
        interaction: discord.Interaction,
        inviteLink: str,
        representativeMember: discord.Member,
    ) -> str:
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
                if existedPartner.status == PartnerStatus.ACTIVE.value:
                    return f"Server {guildName} đã tồn tại trong danh sách partner."

                if existedPartner.status == PartnerStatus.CANCELLED.value:
                    return f"Không thể tạo PN với server {guildName} vì server này đã từng hủy PN."

                return f"Server {guildName} đang có trạng thái partner không hợp lệ."

            representativeDbMember = memberRepository.findByUserId(representativeUserId)
            if representativeDbMember is None:
                return "Người đại diện chưa tồn tại trong server."

            role = self.resolvePartnerRole(bot, interaction)
            if role is None:
                return "Không tìm thấy role partner."

            partnerChannel = await self.resolvePartnerChannel(bot)
            if partnerChannel is None:
                return "Không tìm thấy kênh thông báo partner."

            partnerMessage = await partnerChannel.send(
                self.buildPartnerMessageContent(
                    guildName=guildName,
                    inviteLink=inviteLink,
                    representativeMember=representativeMember,
                    partneredByUser=interaction.user,
                )
            )

            partnerRepository.create({
                "guild_id": guildId,
                "guild_name": guildName,
                "invite_link": inviteLink,
                "representative_user_id": representativeUserId,
                "partnered_by_user_id": partneredByUserId,
                "partner_at": date.today(),
                "status": PartnerStatus.ACTIVE.value,
                "message_id": partnerMessage.id,
            })

            memberRepository.updateIsPartner(representativeUserId, True)

            session.commit()

        await representativeMember.add_roles(role, reason=f"Create partner by {interaction.user.id}")

        return f"Đã tạo partner cho server {guildName} thành công."

    def buildPartnerMessageContent(
        self,
        guildName: str,
        inviteLink: str,
        representativeMember: discord.Member,
        partneredByUser: discord.User,
    ):
        return (
            f"# <a:CS_canhl:1357353968304652491> {guildName} <a:CS_canhr:1357353966341587107>\n\n"
            f"<a:CS_decorate:1366268034603417680> link server: {inviteLink}\n"
            f"<a:CS_decorate:1366268034603417680> Người đại diện: {representativeMember.mention}\n"
            f"<a:CS_decorate:1366268034603417680> Người làm: {partneredByUser.mention}"
        )

    def resolvePartnerRole(self, bot, interaction: discord.Interaction):
        role = interaction.guild.get_role(PARTNER_ROLE_ID) if interaction.guild is not None else None

        if role is not None:
            return role

        guild = bot.get_guild(interaction.guild.id) if interaction.guild is not None else None

        if guild is None:
            return None

        return guild.get_role(PARTNER_ROLE_ID)

    async def resolvePartnerChannel(self, bot):
        channel = bot.get_channel(PARTNER_CHANNEL_ID)

        if channel is not None:
            return channel

        try:
            channel = await bot.fetch_channel(PARTNER_CHANNEL_ID)
        except discord.NotFound:
            return None
        except discord.Forbidden:
            return None
        except discord.HTTPException:
            return None

        if not isinstance(channel, discord.TextChannel):
            return None

        return channel
