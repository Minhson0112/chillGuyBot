from datetime import datetime

from bot.config.database import getDbSession
from bot.enums.lottoEventStatus import LottoEventStatus
from bot.enums.memberPaymentTargetType import MemberPaymentTargetType
from bot.repository.lottoEventRepository import LottoEventRepository
from bot.repository.lottoTicketPurchaseRepository import LottoTicketPurchaseRepository
from bot.repository.memberPaymentTransactionRepository import MemberPaymentTransactionRepository


class LottoTicketPurchaseService:
    def createPendingPurchase(
        self,
        userId: int,
        lottoEventId: int,
        ticketQuantity: int,
    ):
        if ticketQuantity <= 0:
            return {
                "success": False,
                "message": "Số lượng vé lotto phải lớn hơn 0.",
            }

        now = datetime.now()

        with getDbSession() as session:
            lottoEventRepository = LottoEventRepository(session)
            lottoTicketPurchaseRepository = LottoTicketPurchaseRepository(session)
            memberPaymentTransactionRepository = MemberPaymentTransactionRepository(session)

            lottoEvent = lottoEventRepository.findById(lottoEventId)

            if lottoEvent is None:
                return {
                    "success": False,
                    "message": "Không tìm thấy event lotto.",
                }

            if not lottoEvent.is_active or lottoEvent.status != LottoEventStatus.OPEN.value:
                return {
                    "success": False,
                    "message": "Event lotto này hiện không mở bán vé.",
                }

            if lottoEvent.buy_deadline <= now:
                return {
                    "success": False,
                    "message": "Event lotto này đã hết hạn mua vé.",
                }

            pendingPayment = memberPaymentTransactionRepository.findPendingPaymentByUserId(userId)

            if pendingPayment is not None:
                return {
                    "success": False,
                    "message": "Bạn đang có giao dịch khác đang chờ thanh toán. Hãy thanh toán hoặc hủy giao dịch đó trước.",
                }

            paymentAmount = lottoEvent.ticket_price_cowoncy * ticketQuantity

            lottoTicketPurchase = lottoTicketPurchaseRepository.createPendingPurchase(
                userId=userId,
                lottoEventId=lottoEvent.id,
                ticketQuantity=ticketQuantity,
                registeredAt=now,
            )

            memberPaymentTransactionRepository.createPendingPayment(
                userId=userId,
                paymentTargetType=MemberPaymentTargetType.LOTTO_TICKET.value,
                paymentTargetId=lottoTicketPurchase.id,
                requiredCowoncyAmount=paymentAmount,
                requiredChillCoinAmount=None,
                registeredAt=now,
            )

            session.commit()

            return {
                "success": True,
                "lottoEventId": lottoEvent.id,
                "lottoEventName": lottoEvent.name,
                "ticketQuantity": ticketQuantity,
                "paymentAmount": paymentAmount,
            }
