from datetime import datetime

from bot.config.database import getDbSession
from bot.enums.lottoTicketPurchaseStatus import LottoTicketPurchaseStatus
from bot.enums.memberPaymentStatus import MemberPaymentStatus
from bot.enums.memberPaymentTargetType import MemberPaymentTargetType
from bot.repository.lottoTicketPurchaseRepository import LottoTicketPurchaseRepository
from bot.repository.memberPaymentTransactionRepository import MemberPaymentTransactionRepository


class LottoTicketPurchaseCancelService:
    def cancelPendingPurchases(self, userId: int):
        now = datetime.now()

        with getDbSession() as session:
            lottoTicketPurchaseRepository = LottoTicketPurchaseRepository(session)
            memberPaymentTransactionRepository = MemberPaymentTransactionRepository(session)

            pendingPurchases = lottoTicketPurchaseRepository.findPendingPurchasesByUserId(userId)

            if len(pendingPurchases) == 0:
                return {
                    "success": False,
                    "message": "Bạn hiện không có giao dịch mua vé lotto nào đang chờ thanh toán.",
                }

            cancelledPurchases = []

            for pendingPurchase in pendingPurchases:
                cancelledPurchases.append(
                    {
                        "lottoEventId": pendingPurchase.lotto_event_id,
                        "lottoEventName": pendingPurchase.lotto_event.name if pendingPurchase.lotto_event is not None else None,
                        "ticketQuantity": pendingPurchase.ticket_quantity,
                    }
                )

                pendingPurchase.status = LottoTicketPurchaseStatus.CANCELLED.value
                pendingPurchase.payment_type = None
                pendingPurchase.payment_amount = None
                pendingPurchase.paid_at = None
                pendingPurchase.expired_at = None

                pendingPayment = memberPaymentTransactionRepository.findPendingPaymentByTarget(
                    paymentTargetType=MemberPaymentTargetType.LOTTO_TICKET.value,
                    paymentTargetId=pendingPurchase.id,
                )

                if pendingPayment is not None:
                    pendingPayment.status = MemberPaymentStatus.CANCELLED.value
                    pendingPayment.cancelled_at = now

            session.commit()

            return {
                "success": True,
                "message": "Đã hủy giao dịch mua vé lotto thành công.",
                "cancelledPurchases": cancelledPurchases,
            }
