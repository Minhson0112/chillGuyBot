import discord

from bot.config.database import getDbSession
from bot.repository.coupleRepository import CoupleRepository


class CoupleRoleService:
    ROLE_GRANT_REASON = "Set couple role"

    async def setCoupleRole(
        self,
        guild: discord.Guild,
        user1: discord.Member,
        user2: discord.Member,
        role: discord.Role,
    ):
        if user1.id == user2.id:
            return {
                "success": False,
                "message": "Hai member phải khác nhau.",
            }

        if user1.bot or user2.bot:
            return {
                "success": False,
                "message": "Không thể set couple role cho bot.",
            }

        if role.is_default():
            return {
                "success": False,
                "message": "Không thể cấp role @everyone.",
            }

        if role.managed:
            return {
                "success": False,
                "message": "Không thể cấp managed role.",
            }

        if guild.me is None:
            return {
                "success": False,
                "message": "Không thể xác định member của bot trong server.",
            }

        if role >= guild.me.top_role:
            return {
                "success": False,
                "message": "Bot không thể cấp role này vì role cao hơn hoặc bằng role của bot.",
            }

        with getDbSession() as session:
            coupleRepository = CoupleRepository(session)
            couple = coupleRepository.findActiveByPair(
                user1Id=user1.id,
                user2Id=user2.id,
            )

            if couple is None:
                return {
                    "success": False,
                    "message": "Không tìm thấy couple active của hai member này.",
                }

            addedUser1Role = False

            try:
                if role not in user1.roles:
                    await user1.add_roles(
                        role,
                        reason=self.ROLE_GRANT_REASON,
                    )
                    addedUser1Role = True

                if role not in user2.roles:
                    await user2.add_roles(
                        role,
                        reason=self.ROLE_GRANT_REASON,
                    )
            except discord.Forbidden:
                session.rollback()
                await self.rollbackGrantedRole(user1, role, addedUser1Role)
                return {
                    "success": False,
                    "message": "Bot không có quyền cấp role này.",
                }
            except discord.HTTPException:
                session.rollback()
                await self.rollbackGrantedRole(user1, role, addedUser1Role)
                return {
                    "success": False,
                    "message": "Discord xảy ra lỗi khi cấp role.",
                }

            coupleRepository.setCoupleRoleId(couple, role.id)
            session.commit()

        return {
            "success": True,
            "message": f"Đã cấp {role.mention} cho {user1.mention} và {user2.mention}.",
        }

    async def rollbackGrantedRole(
        self,
        member: discord.Member,
        role: discord.Role,
        shouldRollback: bool,
    ):
        if not shouldRollback:
            return

        try:
            await member.remove_roles(
                role,
                reason="Rollback failed couple role set",
            )
        except discord.HTTPException:
            pass
