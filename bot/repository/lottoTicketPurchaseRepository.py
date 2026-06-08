from bot.enums.lottoTicketPurchaseStatus import LottoTicketPurchaseStatus
from bot.models.lottoEvent import LottoEvent
from bot.models.lottoTicketPurchase import LottoTicketPurchase


class LottoTicketPurchaseRepository:
    def __init__(self, session):
        self.session = session

    def createPendingPurchase(
        self,
        userId: int,
        lottoEventId: int,
        ticketQuantity: int,
        registeredAt,
    ):
        lottoTicketPurchase = LottoTicketPurchase(
            user_id=userId,
            lotto_event_id=lottoEventId,
            ticket_quantity=ticketQuantity,
            status=LottoTicketPurchaseStatus.PENDING_PAYMENT.value,
            registered_at=registeredAt,
        )

        self.session.add(lottoTicketPurchase)
        self.session.flush()

        return lottoTicketPurchase

    def findPendingPurchasesByUserId(self, userId: int):
        return (
            self.session.query(LottoTicketPurchase)
            .join(LottoEvent, LottoEvent.id == LottoTicketPurchase.lotto_event_id)
            .filter(
                LottoTicketPurchase.user_id == userId,
                LottoTicketPurchase.status == LottoTicketPurchaseStatus.PENDING_PAYMENT.value,
            )
            .all()
        )
