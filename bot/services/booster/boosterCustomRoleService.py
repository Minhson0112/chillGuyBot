import discord

from bot.config.database import getDbSession
from bot.repository.boosterCustomRoleRepository import BoosterCustomRoleRepository
from bot.repository.memberRepository import MemberRepository


class BoosterCustomRoleService:
    ROLE_GRANT_REASON = "Quyền lợi booster"

    async def setRole(self, interaction: discord.Interaction, target: discord.Member, roleIdText: str):
        if interaction.guild is None:
            return {
                "success": False,
                "message": "Lệnh này chỉ có thể dùng trong server.",
            }

        if not isinstance(interaction.user, discord.Member):
            return {
                "success": False,
                "message": "Không thể xác thực người cấp role.",
            }

        normalizedRoleId = roleIdText.strip()

        if not normalizedRoleId.isdigit():
            return {
                "success": False,
                "message": "Role id không hợp lệ.",
            }

        roleId = int(normalizedRoleId)
        role = interaction.guild.get_role(roleId)

        if role is None:
            return {
                "success": False,
                "message": "Không tìm thấy role trong server.",
            }

        if role.managed:
            return {
                "success": False,
                "message": "Không thể cấp managed role.",
            }

        if interaction.guild.me is None:
            return {
                "success": False,
                "message": "Không thể xác định member của bot trong server.",
            }

        if role >= interaction.guild.me.top_role:
            return {
                "success": False,
                "message": "Bot không thể cấp role này vì role cao hơn hoặc bằng role của bot.",
            }

        if target.bot:
            return {
                "success": False,
                "message": "Không thể cấp custom role booster cho bot.",
            }

        with getDbSession() as session:
            memberRepository = MemberRepository(session)
            boosterCustomRoleRepository = BoosterCustomRoleRepository(session)

            grantedByMember = memberRepository.findByUserId(interaction.user.id)
            targetMember = memberRepository.findByUserId(target.id)

            if grantedByMember is None:
                return {
                    "success": False,
                    "message": "Người cấp role chưa tồn tại trong database. Hãy load member trước.",
                }

            if targetMember is None:
                return {
                    "success": False,
                    "message": "Member được cấp role chưa tồn tại trong database. Hãy load member trước.",
                }

            existingCustomRole = boosterCustomRoleRepository.findActiveByTargetUserIdAndRoleId(
                target.id,
                roleId,
            )

            if existingCustomRole is not None:
                return {
                    "success": False,
                    "message": "Custom role này đã được lưu active cho member này.",
                }

            boosterCustomRoleRepository.createActive(
                grantedByUserId=interaction.user.id,
                targetUserId=target.id,
                roleId=roleId,
            )

            try:
                if role not in target.roles:
                    await target.add_roles(
                        role,
                        reason=self.ROLE_GRANT_REASON,
                    )
            except discord.Forbidden:
                session.rollback()
                return {
                    "success": False,
                    "message": "Bot không có quyền cấp role này.",
                }
            except discord.HTTPException:
                session.rollback()
                return {
                    "success": False,
                    "message": "Discord xảy ra lỗi khi cấp role.",
                }

            session.commit()

        return {
            "success": True,
            "message": f"Đã cấp {role.mention} cho {target.mention}.",
        }
