from bot.config.database import getDbSession
from bot.enums.lottoEventStatus import LottoEventStatus
from bot.repository.lottoEventRepository import LottoEventRepository
from bot.repository.lottoTicketRepository import LottoTicketRepository


class MyLottoService:
    def findMyLatestOpenEventTickets(self, userId: int):
        with getDbSession() as session:
            lottoEventRepository = LottoEventRepository(session)
            lottoTicketRepository = LottoTicketRepository(session)

            lottoEvent = lottoEventRepository.findLatestEvent()

            if lottoEvent is None or lottoEvent.status != LottoEventStatus.OPEN.value:
                return {
                    "success": False,
                    "message": "Hiện tại Chill Station đang không có event lotto nào.",
                }

            tickets = lottoTicketRepository.findByEventIdAndUserId(
                lottoEventId=lottoEvent.id,
                userId=userId,
            )

            return {
                "success": True,
                "lottoEventId": lottoEvent.id,
                "lottoEventName": lottoEvent.name,
                "tickets": [
                    [
                        ticket.number_1,
                        ticket.number_2,
                        ticket.number_3,
                        ticket.number_4,
                        ticket.number_5,
                    ]
                    for ticket in tickets
                ],
            }
