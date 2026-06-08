from bot.config.database import getDbSession
from bot.enums.lottoEventStatus import LottoEventStatus
from bot.repository.lottoEventRepository import LottoEventRepository


class CloseLottoEventService:
    def closeLottoEvent(self, lottoEventId: int):
        with getDbSession() as session:
            lottoEventRepository = LottoEventRepository(session)
            lottoEvent = lottoEventRepository.findById(lottoEventId)

            if lottoEvent is None:
                return {
                    "success": False,
                    "message": "Không tìm thấy event lotto.",
                }

            if lottoEvent.status == LottoEventStatus.CLOSED.value:
                return {
                    "success": False,
                    "message": "Event lotto này đã được đóng trước đó.",
                }

            lottoEventRepository.closeEvent(lottoEvent)
            session.commit()

            return {
                "success": True,
                "message": "Đã đóng event lotto thành công.",
                "lottoEventId": lottoEvent.id,
                "lottoEventName": lottoEvent.name,
            }
