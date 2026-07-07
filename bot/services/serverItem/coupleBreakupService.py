import discord

from bot.config.database import getDbSession
from bot.repository.coupleRepository import CoupleRepository


class CoupleBreakupService:
    ROLE_DELETE_REASON = "Couple breakup"

    async def breakupCurrentCouple(self, guild: discord.Guild, userId: int):
        with getDbSession() as session:
            coupleRepository = CoupleRepository(session)
            couple = coupleRepository.findActiveByUserId(userId)

            if couple is None:
                return {
                    "success": False,
                    "message": "Bạn hiện không có mối quan hệ nào để chia tay.",
                }

            partnerUserId = couple.user_2_id if couple.user_1_id == userId else couple.user_1_id
            roleId = couple.couple_role_id
            role = guild.get_role(roleId) if roleId is not None else None

            if role is not None:
                try:
                    await role.delete(reason=self.ROLE_DELETE_REASON)
                except discord.Forbidden:
                    return {
                        "success": False,
                        "message": "Bot không có quyền xóa couple role.",
                    }
                except discord.HTTPException:
                    return {
                        "success": False,
                        "message": "Discord xảy ra lỗi khi xóa couple role.",
                    }

            coupleRepository.breakupCouple(couple)
            session.commit()

            return {
                "success": True,
                "coupleId": couple.id,
                "partnerUserId": partnerUserId,
            }
