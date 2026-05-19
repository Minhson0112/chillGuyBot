import discord

from bot.config.database import getDbSession
from bot.config.roles import MOD_ROLE_IDS
from bot.repository.memberRepository import MemberRepository


class MemberModService:
    async def setMod(self, interaction: discord.Interaction, target: discord.Member):
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

        modRole = interaction.guild.get_role(MOD_ROLE_IDS["mod"])

        if modRole is None:
            return {
                "success": False,
                "message": "Không tìm thấy role mod trong server.",
            }

        with getDbSession() as session:
            memberRepository = MemberRepository(session)
            member = memberRepository.setModPermission(target.id)

            if member is None:
                return {
                    "success": False,
                    "message": "Member này chưa tồn tại trong database. Hãy load member trước.",
                }

            session.commit()

        if modRole not in target.roles:
            try:
                await target.add_roles(
                    modRole,
                    reason=f"Set mod by {interaction.user}",
                )
            except discord.Forbidden:
                return {
                    "success": False,
                    "message": "Đã cập nhật database nhưng bot không có quyền add role mod.",
                }
            except discord.HTTPException:
                return {
                    "success": False,
                    "message": "Đã cập nhật database nhưng xảy ra lỗi khi add role mod.",
                }

        return {
            "success": True,
            "message": f"Đã set mod cho {target.mention}.",
        }

    async def removeMod(self, interaction: discord.Interaction, target: discord.Member):
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

        modRole = interaction.guild.get_role(MOD_ROLE_IDS["mod"])

        if modRole is None:
            return {
                "success": False,
                "message": "Không tìm thấy role mod trong server.",
            }

        with getDbSession() as session:
            memberRepository = MemberRepository(session)
            member = memberRepository.removeModPermission(target.id)

            if member is None:
                return {
                    "success": False,
                    "message": "Member này chưa tồn tại trong database. Hãy load member trước.",
                }

            session.commit()

        if modRole in target.roles:
            try:
                await target.remove_roles(
                    modRole,
                    reason=f"Remove mod by {interaction.user}",
                )
            except discord.Forbidden:
                return {
                    "success": False,
                    "message": "Đã cập nhật database nhưng bot không có quyền remove role mod.",
                }
            except discord.HTTPException:
                return {
                    "success": False,
                    "message": "Đã cập nhật database nhưng xảy ra lỗi khi remove role mod.",
                }

        return {
            "success": True,
            "message": f"Đã gỡ mod của {target.mention}.",
        }

    def hasOwnerRole(self, member: discord.Member):
        ownerRoleId = MOD_ROLE_IDS["owner"]

        return any(role.id == ownerRoleId for role in member.roles)