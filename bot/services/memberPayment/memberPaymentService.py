from bot.config.database import getDbSession
from bot.repository.memberPaymentTransactionRepository import MemberPaymentTransactionRepository


class MemberPaymentService:
    def findPendingPaymentByUserId(self, userId: int):
        with getDbSession() as session:
            memberPaymentTransactionRepository = MemberPaymentTransactionRepository(session)
            pendingPayment = memberPaymentTransactionRepository.findPendingPaymentByUserId(userId)

            if pendingPayment is None:
                return {
                    "success": False,
                    "message": "Bạn hiện không có giao dịch nào đang chờ thanh toán.",
                }

            return {
                "success": True,
                "memberPaymentTransactionId": pendingPayment.id,
                "paymentTargetType": pendingPayment.payment_target_type,
                "paymentTargetId": pendingPayment.payment_target_id,
            }
