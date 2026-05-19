from datetime import datetime, timedelta, timezone

from bot.config.database import getDbSession
from bot.repository.memberRepository import MemberRepository
from bot.repository.owoExchangeCoinHistoryRepository import OwoExchangeCoinHistoryRepository


class OwoExchangeCoinService:
    COWONCY_PER_CHILL_COIN = 200
    GMT7 = timezone(timedelta(hours=7))

    def exchangeCoin(
        self,
        messageId: int,
        channelId: int,
        senderUserId: int,
        receiverUserId: int,
        cowoncyAmount: int,
    ):
        if cowoncyAmount <= 0:
            return {
                "success": False,
                "message": "Số cowoncy chuyển phải lớn hơn 0.",
            }

        chillCoinAmount = cowoncyAmount // self.COWONCY_PER_CHILL_COIN

        if chillCoinAmount <= 0:
            return {
                "success": False,
                "message": (
                    f"Số cowoncy chuyển chưa đủ để đổi coin. "
                    f"Tỉ lệ hiện tại là **{self.COWONCY_PER_CHILL_COIN:,}** cowoncy = **1** <:cs_coin:1495116560191324383> chill coin."
                ),
            }

        with getDbSession() as session:
            memberRepository = MemberRepository(session)
            owoExchangeCoinHistoryRepository = OwoExchangeCoinHistoryRepository(session)

            existingHistory = owoExchangeCoinHistoryRepository.findByMessageId(messageId)

            if existingHistory is not None:
                return {
                    "success": False,
                    "message": "Giao dịch này đã được xử lý trước đó.",
                }

            senderMember = memberRepository.findByUserId(senderUserId)

            if senderMember is None:
                return {
                    "success": False,
                    "message": "Không tìm thấy dữ liệu member của người chuyển.",
                }

            senderMember.chill_coin += chillCoinAmount

            owoExchangeCoinHistoryRepository.create(
                messageId=messageId,
                channelId=channelId,
                senderUserId=senderUserId,
                receiverUserId=receiverUserId,
                cowoncyAmount=cowoncyAmount,
                transferredAt=self.getNowGmt7(),
            )

            session.commit()

            return {
                "success": True,
                "chillCoinAmount": chillCoinAmount,
            }

    def getNowGmt7(self):
        return datetime.now(self.GMT7).replace(tzinfo=None)