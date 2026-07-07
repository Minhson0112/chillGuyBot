from datetime import datetime

from bot.config.database import getDbSession
from bot.enums.memberPaymentStatus import MemberPaymentStatus
from bot.enums.memberPaymentTargetType import MemberPaymentTargetType
from bot.enums.serverItemPurchaseStatus import ServerItemPurchaseStatus
from bot.helper.serverItemHelper import getServerItemEmoji
from bot.repository.memberPaymentTransactionRepository import MemberPaymentTransactionRepository
from bot.repository.serverItemPurchaseRepository import ServerItemPurchaseRepository


class ServerItemPurchaseCancelService:
    def cancelPendingPurchases(self, userId: int):
        now = datetime.now()

        with getDbSession() as session:
            memberPaymentTransactionRepository = MemberPaymentTransactionRepository(session)
            serverItemPurchaseRepository = ServerItemPurchaseRepository(session)

            pendingPurchases = serverItemPurchaseRepository.findPendingPurchasesByUserId(userId)

            if len(pendingPurchases) == 0:
                return {
                    "success": False,
                    "message": "Bạn hiện không có giao dịch love shop nào đang chờ thanh toán.",
                }

            cancelledItems = []

            for pendingPurchase in pendingPurchases:
                if pendingPurchase.item is not None:
                    cancelledItems.append({
                        "name": pendingPurchase.item.name,
                        "emoji": getServerItemEmoji(pendingPurchase.item),
                        "quantity": pendingPurchase.quantity,
                    })

                pendingPurchase.status = ServerItemPurchaseStatus.CANCELLED.value
                pendingPurchase.payment_type = None
                pendingPurchase.payment_amount = None
                pendingPurchase.paid_at = None
                pendingPurchase.expired_at = None

                pendingPayment = memberPaymentTransactionRepository.findPendingPaymentByTarget(
                    paymentTargetType=MemberPaymentTargetType.SERVER_ITEM.value,
                    paymentTargetId=pendingPurchase.id,
                )

                if pendingPayment is not None:
                    pendingPayment.status = MemberPaymentStatus.CANCELLED.value
                    pendingPayment.cancelled_at = now

            session.commit()

            return {
                "success": True,
                "message": "Đã hủy giao dịch love shop thành công.",
                "cancelledItems": cancelledItems,
            }
