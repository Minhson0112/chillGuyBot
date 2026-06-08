from bot.models.lottoTicket import LottoTicket


class LottoTicketRepository:
    def __init__(self, session):
        self.session = session

    def create(
        self,
        lottoEventId: int,
        lottoTicketPurchaseId: int,
        userId: int,
        numbers: list[int],
    ):
        lottoTicket = LottoTicket(
            lotto_event_id=lottoEventId,
            lotto_ticket_purchase_id=lottoTicketPurchaseId,
            user_id=userId,
            number_1=numbers[0],
            number_2=numbers[1],
            number_3=numbers[2],
            number_4=numbers[3],
            number_5=numbers[4],
        )

        self.session.add(lottoTicket)
        self.session.flush()

        return lottoTicket

    def findByEventIdAndUserId(self, lottoEventId: int, userId: int):
        return (
            self.session.query(LottoTicket)
            .filter(
                LottoTicket.lotto_event_id == lottoEventId,
                LottoTicket.user_id == userId,
            )
            .order_by(LottoTicket.id.asc())
            .all()
        )
