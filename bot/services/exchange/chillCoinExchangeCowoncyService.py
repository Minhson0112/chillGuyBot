from datetime import datetime, timedelta, timezone

from bot.helper.numberFormatHelper import formatNumber
from bot.config.database import getDbSession
from bot.config.emoji import FARM_GAME_EMOJI
from bot.repository.chillCoinExchangeCowoncyHistoryRepository import ChillCoinExchangeCowoncyHistoryRepository
from bot.repository.memberRepository import MemberRepository


class ChillCoinExchangeCowoncyService:
    COWONCY_PER_CHILL_COIN = 150
    WEEKLY_COWONCY_LIMIT = 1000000
    EXCHANGE_LIMIT_DAYS = 7
    COWONCY_EMOJI = "<:OwO:1503021935724859473>"
    GMT7 = timezone(timedelta(hours=7))

    def exchange(
        self,
        senderUserId: int,
        receiverUserId: int,
        chillCoinAmount: int,
    ):
        if chillCoinAmount is None or chillCoinAmount <= 0:
            return {
                "success": False,
                "message": "Số chill coin muốn đổi phải lớn hơn 0.",
            }

        cowoncyAmount = chillCoinAmount * self.COWONCY_PER_CHILL_COIN

        if cowoncyAmount > self.WEEKLY_COWONCY_LIMIT:
            return {
                "success": False,
                "message": self.buildSingleExchangeLimitExceededMessage(),
            }

        with getDbSession() as session:
            memberRepository = MemberRepository(session)
            historyRepository = ChillCoinExchangeCowoncyHistoryRepository(session)

            senderMember = memberRepository.findByUserId(senderUserId)

            if senderMember is None:
                return {
                    "success": False,
                    "message": "Không tìm thấy dữ liệu member của người chuyển cowoncy.",
                }

            receiverMember = memberRepository.findByUserId(receiverUserId)

            if receiverMember is None:
                return {
                    "success": False,
                    "message": "Không tìm thấy dữ liệu member của người đổi tiền.",
                }

            chillCoinEmoji = FARM_GAME_EMOJI["chill_coin"]

            if receiverMember.chill_coin < chillCoinAmount:
                return {
                    "success": False,
                    "message": (
                        f"{self.getMemberDisplayName(receiverMember)} không đủ {chillCoinEmoji} để đổi. "
                        f"Muốn đổi **{formatNumber(chillCoinAmount)}** {chillCoinEmoji}, "
                        f"hiện có **{formatNumber(receiverMember.chill_coin)}** {chillCoinEmoji}."
                    ),
                }

            now = self.getNowGmt7()
            limitStartedAt = now - timedelta(days=self.EXCHANGE_LIMIT_DAYS)
            recentHistories = historyRepository.findByReceiverUserIdTransferredAtFrom(
                receiverUserId=receiverUserId,
                transferredAtFrom=limitStartedAt,
            )
            receivedCowoncyAmount = self.calculateCowoncyAmountFromHistories(recentHistories)
            remainingCowoncyAmount = self.WEEKLY_COWONCY_LIMIT - receivedCowoncyAmount

            if cowoncyAmount > remainingCowoncyAmount:
                nextExchangeAt = self.getNextExchangeAt(
                    recentHistories=recentHistories,
                    receivedCowoncyAmount=receivedCowoncyAmount,
                    requestedCowoncyAmount=cowoncyAmount,
                    now=now,
                )

                return {
                    "success": False,
                    "message": self.buildWeeklyLimitExceededMessage(
                        remainingCowoncyAmount=max(remainingCowoncyAmount, 0),
                        nextExchangeAt=nextExchangeAt,
                    ),
                }

            receiverMember.chill_coin -= chillCoinAmount

            historyRepository.create(
                senderUserId=senderUserId,
                receiverUserId=receiverUserId,
                chillCoinAmount=chillCoinAmount,
                cowoncyAmount=cowoncyAmount,
                transferredAt=now,
            )

            session.commit()

            return {
                "success": True,
                "chillCoinAmount": chillCoinAmount,
                "cowoncyAmount": cowoncyAmount,
            }

    def getNowGmt7(self):
        return datetime.now(self.GMT7).replace(tzinfo=None)

    def getExchangeStatus(self, receiverUserId: int):
        with getDbSession() as session:
            historyRepository = ChillCoinExchangeCowoncyHistoryRepository(session)

            now = self.getNowGmt7()
            limitStartedAt = now - timedelta(days=self.EXCHANGE_LIMIT_DAYS)
            recentHistories = historyRepository.findByReceiverUserIdTransferredAtFrom(
                receiverUserId=receiverUserId,
                transferredAtFrom=limitStartedAt,
            )
            receivedCowoncyAmount = self.calculateCowoncyAmountFromHistories(recentHistories)
            remainingCowoncyAmount = max(self.WEEKLY_COWONCY_LIMIT - receivedCowoncyAmount, 0)
            remainingChillCoinAmount = remainingCowoncyAmount // self.COWONCY_PER_CHILL_COIN

            return {
                "remainingChillCoinAmount": remainingChillCoinAmount,
                "remainingCowoncyAmount": remainingCowoncyAmount,
                "resetAt": self.getNextResetAt(
                    recentHistories=recentHistories,
                    now=now,
                ),
            }

    def calculateCowoncyAmountFromHistories(self, recentHistories):
        return sum(history.cowoncy_amount for history in recentHistories)

    def getNextExchangeAt(
        self,
        recentHistories,
        receivedCowoncyAmount: int,
        requestedCowoncyAmount: int,
        now,
    ):
        runningReceivedCowoncyAmount = receivedCowoncyAmount

        for history in recentHistories:
            runningReceivedCowoncyAmount -= history.cowoncy_amount
            nextExchangeAt = history.transferred_at + timedelta(days=self.EXCHANGE_LIMIT_DAYS)

            if runningReceivedCowoncyAmount + requestedCowoncyAmount <= self.WEEKLY_COWONCY_LIMIT:
                return nextExchangeAt

        return now + timedelta(days=self.EXCHANGE_LIMIT_DAYS)

    def getNextResetAt(
        self,
        recentHistories,
        now,
    ):
        if len(recentHistories) == 0:
            return now

        return recentHistories[0].transferred_at + timedelta(days=self.EXCHANGE_LIMIT_DAYS)

    def buildWeeklyLimitExceededMessage(
        self,
        remainingCowoncyAmount: int,
        nextExchangeAt,
    ):
        nextExchangeAtText = nextExchangeAt.strftime("%d/%m/%Y %H:%M")
        remainingChillCoinAmount = remainingCowoncyAmount // self.COWONCY_PER_CHILL_COIN
        chillCoinEmoji = FARM_GAME_EMOJI["chill_coin"]

        return (
            f"User này chỉ còn có thể đổi thêm **{formatNumber(remainingCowoncyAmount)}** {self.COWONCY_EMOJI} "
            f"trong tuần này, tương đương **{formatNumber(remainingChillCoinAmount)}** {chillCoinEmoji}.\n"
            f"Hãy quay lại vào **{nextExchangeAtText} (GMT+7)**."
        )

    def buildSingleExchangeLimitExceededMessage(self):
        chillCoinEmoji = FARM_GAME_EMOJI["chill_coin"]
        maxChillCoinAmount = self.WEEKLY_COWONCY_LIMIT // self.COWONCY_PER_CHILL_COIN

        return (
            f"Mỗi tuần chỉ có thể đổi tối đa **{formatNumber(self.WEEKLY_COWONCY_LIMIT)}** {self.COWONCY_EMOJI}, "
            f"tương đương **{formatNumber(maxChillCoinAmount)}** {chillCoinEmoji}."
        )

    def getMemberDisplayName(self, member):
        if member.nick:
            return member.nick

        if member.global_name:
            return member.global_name

        return member.username
