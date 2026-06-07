from datetime import datetime, timedelta, timezone

from bot.config.database import getDbSession
from bot.repository.lottoEventRepository import LottoEventRepository


class CreateLottoEventService:
    GMT7 = timezone(timedelta(hours=7))
    DATETIME_FORMAT = "%Y-%m-%d %H:%M"

    def createLottoEvent(
        self,
        name: str,
        ticketPriceCowoncy: int,
        buyDeadlineText: str,
        drawAtText: str,
    ):
        name = name.strip()

        if name == "":
            return {
                "success": False,
                "message": "Tên event lotto không được để trống.",
            }

        if ticketPriceCowoncy <= 0:
            return {
                "success": False,
                "message": "Giá mỗi vé lotto phải lớn hơn 0.",
            }

        buyDeadline = self.parseDatetime(buyDeadlineText)

        if buyDeadline is None:
            return {
                "success": False,
                "message": "Ngày hết hạn mua vé không hợp lệ. Vui lòng nhập theo format `YYYY-MM-DD HH:mm`.",
            }

        drawAt = self.parseDatetime(drawAtText)

        if drawAt is None:
            return {
                "success": False,
                "message": "Ngày quay thưởng không hợp lệ. Vui lòng nhập theo format `YYYY-MM-DD HH:mm`.",
            }

        now = datetime.now(self.GMT7).replace(tzinfo=None)

        if buyDeadline <= now:
            return {
                "success": False,
                "message": "Ngày hết hạn mua vé phải lớn hơn thời gian hiện tại.",
            }

        if drawAt <= buyDeadline:
            return {
                "success": False,
                "message": "Ngày quay thưởng phải lớn hơn ngày hết hạn mua vé.",
            }

        with getDbSession() as session:
            lottoEventRepository = LottoEventRepository(session)
            lottoEvent = lottoEventRepository.create(
                name=name,
                ticketPriceCowoncy=ticketPriceCowoncy,
                buyDeadline=buyDeadline,
                drawAt=drawAt,
            )

            session.commit()

            return {
                "success": True,
                "lottoEventId": lottoEvent.id,
                "name": lottoEvent.name,
                "ticketPriceCowoncy": lottoEvent.ticket_price_cowoncy,
                "buyDeadline": lottoEvent.buy_deadline,
                "drawAt": lottoEvent.draw_at,
                "message": f"Đã tạo event lotto **#{lottoEvent.id}** thành công.",
            }

    def parseDatetime(self, datetimeText: str):
        try:
            return datetime.strptime(datetimeText.strip(), self.DATETIME_FORMAT)
        except ValueError:
            return None
