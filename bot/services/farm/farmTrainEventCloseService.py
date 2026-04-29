from bot.config.database import getDbSession
from bot.repository.farmRepository import FarmRepository
from bot.repository.farmTrainEventRepository import FarmTrainEventRepository


class FarmTrainEventCloseService:
    def closeTrainEvent(
        self,
        trainEventId: int,
    ):
        if trainEventId is None or trainEventId <= 0:
            return {
                "success": False,
                "message": "ID sự kiện tàu hỏa không hợp lệ.",
            }

        with getDbSession() as session:
            farmRepository = FarmRepository(session)
            farmTrainEventRepository = FarmTrainEventRepository(session)

            farmTrainEvent = farmTrainEventRepository.findById(trainEventId)

            if farmTrainEvent is None:
                return {
                    "success": False,
                    "message": f"Không tìm thấy sự kiện tàu hỏa với ID **{trainEventId}**.",
                }

            if farmTrainEvent.closed_at is not None:
                return {
                    "success": False,
                    "message": f"Sự kiện tàu hỏa **#{trainEventId}** đã được đóng trước đó.",
                }

            farmTrainEventRepository.closeEvent(farmTrainEvent)
            farmRepository.updateAllTrainEventFlag(False)

            session.commit()

            return {
                "success": True,
                "message": (
                    f"Đã đóng sự kiện tàu hỏa **#{trainEventId}**.\n"
                    f"Tàu hỏa đã biến mất khỏi toàn bộ farm."
                ),
            }