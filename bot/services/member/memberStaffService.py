import discord

from bot.config.database import getDbSession
from bot.config.roles import MOD_ROLE_IDS
from bot.repository.memberRepository import MemberRepository


class MemberStaffService:
    async def setStaff(self, interaction: discord.Interaction, target: discord.Member):
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

        staffRole = interaction.guild.get_role(MOD_ROLE_IDS["staff"])

        if staffRole is None:
            return {
                "success": False,
                "message": "Không tìm thấy role staff trong server.",
            }

        with getDbSession() as session:
            memberRepository = MemberRepository(session)
            member = memberRepository.setStaffPermission(target.id)

            if member is None:
                return {
                    "success": False,
                    "message": "Member này chưa tồn tại trong database. Hãy load member trước.",
                }

            session.commit()

        if staffRole not in target.roles:
            try:
                await target.add_roles(
                    staffRole,
                    reason=f"Set staff by {interaction.user}",
                )
            except discord.Forbidden:
                return {
                    "success": False,
                    "message": "Đã cập nhật database nhưng bot không có quyền add role staff.",
                }
            except discord.HTTPException:
                return {
                    "success": False,
                    "message": "Đã cập nhật database nhưng xảy ra lỗi khi add role staff.",
                }

        return {
            "success": True,
            "message": f"Đã set staff cho {target.mention}.",
        }

    async def removeStaff(self, interaction: discord.Interaction, target: discord.Member):
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

        staffRole = interaction.guild.get_role(MOD_ROLE_IDS["staff"])

        if staffRole is None:
            return {
                "success": False,
                "message": "Không tìm thấy role staff trong server.",
            }

        with getDbSession() as session:
            memberRepository = MemberRepository(session)
            member = memberRepository.removeStaffPermission(target.id)

            if member is None:
                return {
                    "success": False,
                    "message": "Member này chưa tồn tại trong database. Hãy load member trước.",
                }

            session.commit()

        if staffRole in target.roles:
            try:
                await target.remove_roles(
                    staffRole,
                    reason=f"Remove staff by {interaction.user}",
                )
            except discord.Forbidden:
                return {
                    "success": False,
                    "message": "Đã cập nhật database nhưng bot không có quyền remove role staff.",
                }
            except discord.HTTPException:
                return {
                    "success": False,
                    "message": "Đã cập nhật database nhưng xảy ra lỗi khi remove role staff.",
                }

        return {
            "success": True,
            "message": f"Đã gỡ staff của {target.mention}.",
        }

    def hasOwnerRole(self, member: discord.Member):
        ownerRoleId = MOD_ROLE_IDS["owner"]

        return any(role.id == ownerRoleId for role in member.roles)