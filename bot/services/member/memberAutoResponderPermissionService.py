import discord

from bot.config.database import getDbSession
from bot.config.roles import MOD_ROLE_IDS
from bot.repository.memberRepository import MemberRepository


class MemberAutoResponderPermissionService:
    async def setAutoResponderPermission(self, interaction: discord.Interaction, target: discord.Member):
        if interaction.guild is None:
            return {
                "success": False,
                "message": "Lệnh này chỉ có thể dùng trong server.",
            }

        if not isinstance(interaction.user, discord.Member):
            return {
                "success": False,
                "message": "Không thể xác thực quyền của bạn.",
            }

        if not self.hasOwnerRole(interaction.user):
            return {
                "success": False,
                "message": "Bạn không có quyền dùng lệnh này.",
            }

        with getDbSession() as session:
            memberRepository = MemberRepository(session)
            member = memberRepository.setAutoResponderPermission(target.id)

            if member is None:
                return {
                    "success": False,
                    "message": "Member này chưa tồn tại trong database. Hãy load member trước.",
                }

            session.commit()

        return {
            "success": True,
            "message": f"Đã cấp quyền tạo auto response cho {target.mention}.",
        }

    async def removeAutoResponderPermission(self, interaction: discord.Interaction, target: discord.Member):
        if interaction.guild is None:
            return {
                "success": False,
                "message": "Lệnh này chỉ có thể dùng trong server.",
            }

        if not isinstance(interaction.user, discord.Member):
            return {
                "success": False,
                "message": "Không thể xác thực quyền của bạn.",
            }

        if not self.hasOwnerRole(interaction.user):
            return {
                "success": False,
                "message": "Bạn không có quyền dùng lệnh này.",
            }

        with getDbSession() as session:
            memberRepository = MemberRepository(session)
            member = memberRepository.removeAutoResponderPermission(target.id)

            if member is None:
                return {
                    "success": False,
                    "message": "Member này chưa tồn tại trong database. Hãy load member trước.",
                }

            session.commit()

        return {
            "success": True,
            "message": f"Đã xóa quyền tạo auto response của {target.mention}.",
        }

    def hasOwnerRole(self, member: discord.Member):
        ownerRoleId = MOD_ROLE_IDS["owner"]

        return any(role.id == ownerRoleId for role in member.roles)