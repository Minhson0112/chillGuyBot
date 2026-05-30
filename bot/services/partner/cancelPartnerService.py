import discord

from bot.config.channel import PARTNER_CHANNEL_ID
from bot.config.database import getDbSession
from bot.config.roles import PARTNER_ROLE_ID
from bot.enums.partnerStatus import PartnerStatus
from bot.repository.memberRepository import MemberRepository
from bot.repository.partnerRepository import PartnerRepository


class CancelPartnerService:
    def buildCancelPreview(self, partnerId: int):
        with getDbSession() as session:
            partnerRepository = PartnerRepository(session)
            memberRepository = MemberRepository(session)

            partner = partnerRepository.findById(partnerId)

            if partner is None:
                return {
                    "success": False,
                    "message": "Không tìm thấy server partner với ID này.",
                }

            if partner.status != PartnerStatus.ACTIVE.value:
                return {
                    "success": False,
                    "message": "Server partner này không ở trạng thái active.",
                }

            representativeMember = memberRepository.findByUserId(partner.representative_user_id)
            representativeText = self.buildRepresentativeText(
                representativeUserId=partner.representative_user_id,
                representativeMember=representativeMember,
            )

            return {
                "success": True,
                "partnerId": partner.id,
                "guildName": partner.guild_name,
                "representativeText": representativeText,
            }

    async def cancelPartner(self, bot, guild, partnerId: int):
        with getDbSession() as session:
            partnerRepository = PartnerRepository(session)
            memberRepository = MemberRepository(session)

            partner = partnerRepository.findById(partnerId)

            if partner is None:
                return {
                    "success": False,
                    "message": "Không tìm thấy server partner với ID này.",
                }

            if partner.status != PartnerStatus.ACTIVE.value:
                return {
                    "success": False,
                    "message": "Server partner này không ở trạng thái active.",
                }

            representativeDbMember = memberRepository.findByUserId(partner.representative_user_id)

            deleteResult = await self.deletePartnerMessage(bot, partner.message_id)
            if not deleteResult["success"]:
                return deleteResult

            partnerRepository.updateStatus(partner, PartnerStatus.CANCELLED.value)
            memberRepository.updateIsPartner(partner.representative_user_id, False)

            session.commit()

            representativeUserId = partner.representative_user_id
            guildName = partner.guild_name

        if representativeDbMember is not None and representativeDbMember.leave_at is None:
            await self.removePartnerRole(
                guild=guild,
                userId=representativeUserId,
            )

        return {
            "success": True,
            "message": f"Đã xóa PN cho server {guildName} thành công.",
        }

    def buildRepresentativeText(self, representativeUserId: int, representativeMember):
        if representativeMember is None or representativeMember.leave_at is not None:
            return "đã out server Chill Station"

        return f"<@{representativeUserId}>"

    async def deletePartnerMessage(self, bot, messageId):
        if messageId is None:
            return {
                "success": False,
                "message": "Server partner này chưa có message_id để xóa tin nhắn PN.",
            }

        partnerChannel = await self.resolvePartnerChannel(bot)

        if partnerChannel is None:
            return {
                "success": False,
                "message": "Không tìm thấy kênh partner để xóa tin nhắn PN.",
            }

        try:
            message = await partnerChannel.fetch_message(messageId)
            await message.delete()
        except discord.NotFound:
            return {
                "success": False,
                "message": "Không tìm thấy tin nhắn PN trong kênh partner.",
            }
        except discord.Forbidden:
            return {
                "success": False,
                "message": "Bot không có quyền xóa tin nhắn PN.",
            }
        except discord.HTTPException:
            return {
                "success": False,
                "message": "Đã xảy ra lỗi khi xóa tin nhắn PN.",
            }

        return {
            "success": True,
            "message": "Đã xóa tin nhắn PN.",
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

    async def removePartnerRole(self, guild, userId: int):
        if guild is None:
            return

        role = guild.get_role(PARTNER_ROLE_ID)
        if role is None:
            return

        member = guild.get_member(userId)

        if member is None:
            try:
                member = await guild.fetch_member(userId)
            except discord.NotFound:
                return
            except discord.Forbidden:
                return
            except discord.HTTPException:
                return

        if role not in member.roles:
            return

        try:
            await member.remove_roles(role, reason="Cancel partner")
        except discord.Forbidden:
            return
        except discord.HTTPException:
            return
