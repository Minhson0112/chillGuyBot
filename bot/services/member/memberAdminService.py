import discord

from bot.config.database import getDbSession
from bot.config.roles import MOD_ROLE_IDS
from bot.repository.memberRepository import MemberRepository


class MemberAdminService:
    async def setAdmin(self, interaction: discord.Interaction, target: discord.Member):
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

        adminRole = interaction.guild.get_role(MOD_ROLE_IDS["admin"])

        if adminRole is None:
            return {
                "success": False,
                "message": "Không tìm thấy role admin trong server.",
            }

        with getDbSession() as session:
            memberRepository = MemberRepository(session)
            member = memberRepository.setAdminPermission(target.id)

            if member is None:
                return {
                    "success": False,
                    "message": "Member này chưa tồn tại trong database. Hãy load member trước.",
                }

            session.commit()

        if adminRole not in target.roles:
            try:
                await target.add_roles(
                    adminRole,
                    reason=f"Set admin by {interaction.user}",
                )
            except discord.Forbidden:
                return {
                    "success": False,
                    "message": "Đã cập nhật database nhưng bot không có quyền add role admin.",
                }
            except discord.HTTPException:
                return {
                    "success": False,
                    "message": "Đã cập nhật database nhưng xảy ra lỗi khi add role admin.",
                }

        return {
            "success": True,
            "message": f"Đã set admin cho {target.mention}.",
        }

    async def removeAdmin(self, interaction: discord.Interaction, target: discord.Member):
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

        adminRole = interaction.guild.get_role(MOD_ROLE_IDS["admin"])

        if adminRole is None:
            return {
                "success": False,
                "message": "Không tìm thấy role admin trong server.",
            }

        with getDbSession() as session:
            memberRepository = MemberRepository(session)
            member = memberRepository.removeAdminPermission(target.id)

            if member is None:
                return {
                    "success": False,
                    "message": "Member này chưa tồn tại trong database. Hãy load member trước.",
                }

            session.commit()

        if adminRole in target.roles:
            try:
                await target.remove_roles(
                    adminRole,
                    reason=f"Remove admin by {interaction.user}",
                )
            except discord.Forbidden:
                return {
                    "success": False,
                    "message": "Đã cập nhật database nhưng bot không có quyền remove role admin.",
                }
            except discord.HTTPException:
                return {
                    "success": False,
                    "message": "Đã cập nhật database nhưng xảy ra lỗi khi remove role admin.",
                }

        return {
            "success": True,
            "message": f"Đã gỡ admin của {target.mention}.",
        }

    def hasOwnerRole(self, member: discord.Member):
        ownerRoleId = MOD_ROLE_IDS["owner"]

        return any(role.id == ownerRoleId for role in member.roles)