from bot.config.database import getDbSession
from bot.enums.rolePurchaseStatus import RolePurchaseStatus
from bot.repository.memberRolePurchaseRepository import MemberRolePurchaseRepository


class RoleShopPurchaseCancelService:
    def cancelPendingPurchases(self, userId: int):
        with getDbSession() as session:
            memberRolePurchaseRepository = MemberRolePurchaseRepository(session)

            pendingPurchases = memberRolePurchaseRepository.findPendingPurchasesByUserId(userId)

            if len(pendingPurchases) == 0:
                return {
                    "success": False,
                    "message": "Bạn hiện không có giao dịch mua role nào đang chờ thanh toán.",
                }

            cancelledRoleIds = []

            for pendingPurchase in pendingPurchases:
                if pendingPurchase.role_shop is not None:
                    cancelledRoleIds.append(pendingPurchase.role_shop.role_id)

                pendingPurchase.status = RolePurchaseStatus.CANCELLED.value
                pendingPurchase.payment_type = None
                pendingPurchase.payment_amount = None
                pendingPurchase.paid_at = None
                pendingPurchase.expired_at = None

            session.commit()

            return {
                "success": True,
                "message": "Đã hủy giao dịch mua role thành công.",
                "cancelledRoleIds": cancelledRoleIds,
            }