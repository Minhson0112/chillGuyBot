from datetime import datetime, timedelta, timezone

from bot.config.database import getDbSession
from bot.repository.memberRepository import MemberRepository
from bot.repository.owoExchangeCoinHistoryRepository import OwoExchangeCoinHistoryRepository


class OwoExchangeCoinService:
    COWONCY_PER_CHILL_COIN = 200
    WEEKLY_CHILL_COIN_LIMIT = 5000
    EXCHANGE_LIMIT_DAYS = 7
    CHILL_COIN_EMOJI = "<:cs_coin:1495116560191324383>"
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
                    f"Tỉ lệ hiện tại là **{self.COWONCY_PER_CHILL_COIN:,}** cowoncy = **1** {self.CHILL_COIN_EMOJI} chill coin."
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

            now = self.getNowGmt7()
            limitStartedAt = now - timedelta(days=self.EXCHANGE_LIMIT_DAYS)
            recentHistories = owoExchangeCoinHistoryRepository.findBySenderUserIdTransferredAtFrom(
                senderUserId=senderUserId,
                transferredAtFrom=limitStartedAt,
            )
            receivedChillCoinAmount = self.calculateChillCoinAmountFromHistories(recentHistories)

            if receivedChillCoinAmount + chillCoinAmount > self.WEEKLY_CHILL_COIN_LIMIT:
                nextExchangeAt = self.getNextExchangeAt(
                    recentHistories=recentHistories,
                    receivedChillCoinAmount=receivedChillCoinAmount,
                    requestedChillCoinAmount=chillCoinAmount,
                    now=now,
                )

                return {
                    "success": False,
                    "message": self.buildWeeklyLimitExceededMessage(
                        receivedChillCoinAmount=receivedChillCoinAmount,
                        requestedChillCoinAmount=chillCoinAmount,
                        nextExchangeAt=nextExchangeAt,
                    ),
                }

            senderMember.chill_coin += chillCoinAmount

            owoExchangeCoinHistoryRepository.create(
                messageId=messageId,
                channelId=channelId,
                senderUserId=senderUserId,
                receiverUserId=receiverUserId,
                cowoncyAmount=cowoncyAmount,
                transferredAt=now,
            )

            session.commit()

            return {
                "success": True,
                "chillCoinAmount": chillCoinAmount,
            }

    def getNowGmt7(self):
        return datetime.now(self.GMT7).replace(tzinfo=None)

    def calculateChillCoinAmountFromHistories(self, recentHistories):
        return sum(
            history.cowoncy_amount // self.COWONCY_PER_CHILL_COIN
            for history in recentHistories
        )

    def getNextExchangeAt(
        self,
        recentHistories,
        receivedChillCoinAmount: int,
        requestedChillCoinAmount: int,
        now,
    ):
        runningReceivedChillCoinAmount = receivedChillCoinAmount

        for history in recentHistories:
            runningReceivedChillCoinAmount -= history.cowoncy_amount // self.COWONCY_PER_CHILL_COIN
            nextExchangeAt = history.transferred_at + timedelta(days=self.EXCHANGE_LIMIT_DAYS)

            if runningReceivedChillCoinAmount + requestedChillCoinAmount <= self.WEEKLY_CHILL_COIN_LIMIT:
                return nextExchangeAt

        return now + timedelta(days=self.EXCHANGE_LIMIT_DAYS)

    def buildWeeklyLimitExceededMessage(
        self,
        receivedChillCoinAmount: int,
        requestedChillCoinAmount: int,
        nextExchangeAt,
    ):
        nextExchangeAtText = nextExchangeAt.strftime("%d/%m/%Y %H:%M")

        return (
            f"Bạn đã nhận **{receivedChillCoinAmount:,}/{self.WEEKLY_CHILL_COIN_LIMIT:,}** {self.CHILL_COIN_EMOJI} "
            f"trong {self.EXCHANGE_LIMIT_DAYS} ngày gần đây.\n"
            f"Giao dịch này muốn đổi **{requestedChillCoinAmount:,}** {self.CHILL_COIN_EMOJI} nên đã vượt hạn mức. "
            f"Hãy đổi tiền tiếp vào ngày **{nextExchangeAtText} (GMT+7)**."
        )
