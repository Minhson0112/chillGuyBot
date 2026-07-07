from bot.config.database import getDbSession
from bot.repository.coupleRepository import CoupleRepository


class CoupleBreakupService:
    def breakupCurrentCouple(self, userId: int):
        with getDbSession() as session:
            coupleRepository = CoupleRepository(session)
            couple = coupleRepository.findActiveByUserId(userId)

            if couple is None:
                return {
                    "success": False,
                    "message": "Bạn hiện không có mối quan hệ nào để chia tay.",
                }

            partnerUserId = couple.user_2_id if couple.user_1_id == userId else couple.user_1_id
            coupleRepository.breakupCouple(couple)
            session.commit()

            return {
                "success": True,
                "coupleId": couple.id,
                "partnerUserId": partnerUserId,
            }
