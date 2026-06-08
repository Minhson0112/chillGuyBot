from datetime import datetime

from bot.config.database import getDbSession
from bot.enums.memberPaymentStatus import MemberPaymentStatus
from bot.enums.memberPaymentTargetType import MemberPaymentTargetType
from bot.enums.rolePurchaseStatus import RolePurchaseStatus
from bot.repository.memberPaymentTransactionRepository import MemberPaymentTransactionRepository
from bot.repository.memberRolePurchaseRepository import MemberRolePurchaseRepository


class RoleShopPurchaseCancelService:
    def cancelPendingPurchases(self, userId: int):
        now = datetime.now()

        with getDbSession() as session:
            memberPaymentTransactionRepository = MemberPaymentTransactionRepository(session)
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

                pendingPayment = memberPaymentTransactionRepository.findPendingPaymentByTarget(
                    paymentTargetType=MemberPaymentTargetType.ROLE_SHOP.value,
                    paymentTargetId=pendingPurchase.id,
                )

                if pendingPayment is not None:
                    pendingPayment.status = MemberPaymentStatus.CANCELLED.value
                    pendingPayment.cancelled_at = now

            session.commit()

            return {
                "success": True,
                "message": "Đã hủy giao dịch mua role thành công.",
                "cancelledRoleIds": cancelledRoleIds,
            }
