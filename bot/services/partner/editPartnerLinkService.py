import discord

from bot.config.channel import PARTNER_CHANNEL_ID
from bot.config.database import getDbSession
from bot.enums.partnerStatus import PartnerStatus
from bot.repository.partnerRepository import PartnerRepository
from bot.services.partner.createPartnerService import CreatePartnerService


class EditPartnerLinkService:
    def __init__(self):
        self.createPartnerService = CreatePartnerService()

    async def editPartnerLink(
        self,
        bot,
        interaction: discord.Interaction,
        partnerId: int,
        inviteLink: str,
    ):
        try:
            invite = await bot.fetch_invite(inviteLink, with_counts=True)
        except discord.NotFound:
            return "Link mời không tồn tại hoặc đã hết hạn."
        except discord.HTTPException:
            return "Không thể lấy thông tin từ link mời."

        if invite.guild is None:
            return "Không lấy được thông tin guild từ link mời."

        newGuildId = invite.guild.id
        newGuildName = invite.guild.name

        with getDbSession() as session:
            partnerRepository = PartnerRepository(session)
            partner = partnerRepository.findById(partnerId)

            if partner is None:
                return "Không tìm thấy server partner với ID này."

            if partner.status != PartnerStatus.ACTIVE.value:
                return "Server partner này không ở trạng thái active."

            if partner.guild_id != newGuildId:
                return "Link mới không thuộc server partner hiện tại."

            if partner.message_id is None:
                return "Server partner này chưa có message_id để sửa tin nhắn PN."

            representativeMember = await self.resolveRepresentativeMember(
                guild=interaction.guild,
                userId=partner.representative_user_id,
            )
            if representativeMember is None:
                return "Không tìm thấy người đại diện trong Chill Station."

            fetchMessageResult = await self.fetchPartnerMessage(bot, partner.message_id)
            if not fetchMessageResult["success"]:
                return fetchMessageResult["message"]

            try:
                await fetchMessageResult["messageObject"].edit(
                    content=self.createPartnerService.buildPartnerMessageContent(
                        guildName=newGuildName,
                        inviteLink=inviteLink,
                        representativeMember=representativeMember,
                        partneredByUser=interaction.user,
                    )
                )
            except discord.Forbidden:
                return "Bot không có quyền sửa tin nhắn PN."
            except discord.HTTPException:
                return "Đã xảy ra lỗi khi sửa tin nhắn PN."

            if partner.guild_name != newGuildName:
                partnerRepository.updateGuildName(partner, newGuildName)

            session.commit()

        return f"Đã cập nhật link PN cho server {newGuildName} thành công."

    async def fetchPartnerMessage(self, bot, messageId):
        partnerChannel = await self.resolvePartnerChannel(bot)

        if partnerChannel is None:
            return {
                "success": False,
                "message": "Không tìm thấy kênh partner để sửa tin nhắn PN.",
            }

        try:
            message = await partnerChannel.fetch_message(messageId)
        except discord.NotFound:
            return {
                "success": False,
                "message": "Không tìm thấy tin nhắn PN trong kênh partner.",
            }
        except discord.Forbidden:
            return {
                "success": False,
                "message": "Bot không có quyền xem tin nhắn PN.",
            }
        except discord.HTTPException:
            return {
                "success": False,
                "message": "Đã xảy ra lỗi khi lấy tin nhắn PN.",
            }

        return {
            "success": True,
            "messageObject": message,
        }

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

    async def resolveRepresentativeMember(self, guild, userId: int):
        if guild is None:
            return None

        member = guild.get_member(userId)

        if member is not None:
            return member

        try:
            return await guild.fetch_member(userId)
        except discord.NotFound:
            return None
        except discord.Forbidden:
            return None
        except discord.HTTPException:
            return None
