from datetime import datetime

from bot.config.database import getDbSession
from bot.enums.rolePurchaseStatus import RolePurchaseStatus
from bot.repository.memberRolePurchaseRepository import MemberRolePurchaseRepository


class RoleShopExpireService:
    def findExpiredPurchases(self):
        now = datetime.now()

        with getDbSession() as session:
            memberRolePurchaseRepository = MemberRolePurchaseRepository(session)
            expiredPurchases = memberRolePurchaseRepository.findPaidExpiredPurchases(now)

            return [
                {
                    "id": expiredPurchase.id,
                    "userId": expiredPurchase.user_id,
                    "roleId": expiredPurchase.role_shop.role_id,
                    "expiredAt": expiredPurchase.expired_at,
                }
                for expiredPurchase in expiredPurchases
                if expiredPurchase.role_shop is not None
            ]

    def markExpired(self, memberRolePurchaseId: int):
        with getDbSession() as session:
            memberRolePurchaseRepository = MemberRolePurchaseRepository(session)
            memberRolePurchase = memberRolePurchaseRepository.findById(memberRolePurchaseId)

            if memberRolePurchase is None:
                return {
                    "success": False,
                    "message": "Không tìm thấy giao dịch mua role.",
                }

            if memberRolePurchase.status != RolePurchaseStatus.PAID.value:
                return {
                    "success": False,
                    "message": "Giao dịch không còn ở trạng thái paid.",
                }

            memberRolePurchase.status = RolePurchaseStatus.EXPIRED.value

            session.commit()

            return {
                "success": True,
            }