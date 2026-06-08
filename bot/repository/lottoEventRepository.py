from bot.enums.lottoEventStatus import LottoEventStatus
from bot.models.lottoEvent import LottoEvent


class LottoEventRepository:
    def __init__(self, session):
        self.session = session

    def create(
        self,
        name: str,
        ticketPriceCowoncy: int,
        buyDeadline,
        drawAt,
    ):
        lottoEvent = LottoEvent(
            name=name,
            ticket_price_cowoncy=ticketPriceCowoncy,
            buy_deadline=buyDeadline,
            draw_at=drawAt,
            status=LottoEventStatus.OPEN.value,
            is_active=True,
        )

        self.session.add(lottoEvent)
        self.session.flush()

        return lottoEvent

    def findById(self, lottoEventId: int):
        return (
            self.session.query(LottoEvent)
            .filter(LottoEvent.id == lottoEventId)
            .first()
        )

    def findActiveOpenEvents(self):
        return (
            self.session.query(LottoEvent)
            .filter(
                LottoEvent.is_active.is_(True),
                LottoEvent.status == LottoEventStatus.OPEN.value,
            )
            .all()
        )

    def findLatestEvent(self):
        return (
            self.session.query(LottoEvent)
            .order_by(LottoEvent.id.desc())
            .first()
        )

    def closeEvent(self, lottoEvent):
        lottoEvent.status = LottoEventStatus.CLOSED.value
        return lottoEvent
