import random
from datetime import datetime

from bot.config.database import getDbSession
from bot.enums.lottoTicketPurchaseStatus import LottoTicketPurchaseStatus
from bot.enums.memberPaymentStatus import MemberPaymentStatus
from bot.enums.paymentType import PaymentType
from bot.repository.lottoTicketPurchaseRepository import LottoTicketPurchaseRepository
from bot.repository.lottoTicketRepository import LottoTicketRepository
from bot.repository.memberPaymentTransactionRepository import MemberPaymentTransactionRepository


class LottoTicketPaymentService:
    LOTTO_NUMBER_MIN = 1
    LOTTO_NUMBER_MAX = 99
    LOTTO_NUMBER_COUNT = 5

    def completePayment(
        self,
        memberPaymentTransactionId: int,
        paymentType: str,
        paymentAmount: int,
    ):
        if paymentAmount <= 0:
            return {
                "success": False,
                "message": "Số tiền thanh toán không hợp lệ.",
            }

        if paymentType != PaymentType.COWONCY.value:
            return {
                "success": False,
                "message": "Vé lotto chỉ hỗ trợ thanh toán bằng cowoncy.",
            }

        now = datetime.now()

        with getDbSession() as session:
            memberPaymentTransactionRepository = MemberPaymentTransactionRepository(session)
            lottoTicketPurchaseRepository = LottoTicketPurchaseRepository(session)
            lottoTicketRepository = LottoTicketRepository(session)

            memberPaymentTransaction = memberPaymentTransactionRepository.findById(memberPaymentTransactionId)

            if memberPaymentTransaction is None:
                return {
                    "success": False,
                    "message": "Không tìm thấy giao dịch thanh toán.",
                }

            if memberPaymentTransaction.status != MemberPaymentStatus.PENDING_PAYMENT.value:
                return {
                    "success": False,
                    "message": "Giao dịch thanh toán này không còn ở trạng thái chờ thanh toán.",
                }

            requiredAmount = memberPaymentTransaction.required_cowoncy_amount

            if requiredAmount is None or requiredAmount <= 0:
                return {
                    "success": False,
                    "message": "Không tìm thấy số tiền cần thanh toán của giao dịch mua vé lotto.",
                }

            if paymentAmount < requiredAmount:
                return {
                    "success": False,
                    "message": f"Số tiền thanh toán chưa đủ. Bạn cần thanh toán **{requiredAmount:,}**, hiện tại mới nhận được **{paymentAmount:,}**.",
                    "requiredAmount": requiredAmount,
                    "paymentAmount": paymentAmount,
                }

            lottoTicketPurchase = lottoTicketPurchaseRepository.findById(memberPaymentTransaction.payment_target_id)

            if lottoTicketPurchase is None:
                return {
                    "success": False,
                    "message": "Không tìm thấy giao dịch mua vé lotto.",
                }

            if lottoTicketPurchase.status != LottoTicketPurchaseStatus.PENDING_PAYMENT.value:
                return {
                    "success": False,
                    "message": "Giao dịch mua vé lotto này không còn ở trạng thái chờ thanh toán.",
                }

            createdTickets = []
            createdTicketKeys = set()

            for _ in range(lottoTicketPurchase.ticket_quantity):
                numbers = self.generateUniqueTicketNumbers(createdTicketKeys)
                lottoTicketRepository.create(
                    lottoEventId=lottoTicketPurchase.lotto_event_id,
                    lottoTicketPurchaseId=lottoTicketPurchase.id,
                    userId=lottoTicketPurchase.user_id,
                    numbers=numbers,
                )
                createdTickets.append(numbers)

            lottoTicketPurchase.status = LottoTicketPurchaseStatus.PAID.value
            lottoTicketPurchase.payment_type = paymentType
            lottoTicketPurchase.payment_amount = paymentAmount
            lottoTicketPurchase.paid_at = now

            memberPaymentTransaction.status = MemberPaymentStatus.PAID.value
            memberPaymentTransaction.paid_payment_type = paymentType
            memberPaymentTransaction.paid_amount = paymentAmount
            memberPaymentTransaction.paid_at = now

            session.commit()

            return {
                "success": True,
                "tickets": createdTickets,
                "paymentAmount": paymentAmount,
                "requiredAmount": requiredAmount,
            }

    def generateTicketNumbers(self):
        return sorted(
            random.sample(
                range(self.LOTTO_NUMBER_MIN, self.LOTTO_NUMBER_MAX + 1),
                self.LOTTO_NUMBER_COUNT,
            )
        )

    def generateUniqueTicketNumbers(self, existingTicketKeys: set[tuple[int, ...]]):
        while True:
            numbers = self.generateTicketNumbers()
            ticketKey = tuple(numbers)

            if ticketKey not in existingTicketKeys:
                existingTicketKeys.add(ticketKey)
                return numbers
