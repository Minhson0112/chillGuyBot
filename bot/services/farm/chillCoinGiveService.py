from datetime import datetime, time, timedelta

from bot.helper.numberFormatHelper import formatNumber
from bot.config.database import getDbSession
from bot.config.emoji import FARM_GAME_EMOJI
from bot.enums.chillCoinTransactionType import ChillCoinTransactionType
from bot.repository.chillCoinTransactionRepository import ChillCoinTransactionRepository
from bot.repository.memberRepository import MemberRepository


class ChillCoinGiveService:
    DAILY_RECEIVE_LIMIT = 5000
    TRANSACTION_TYPE = ChillCoinTransactionType.TRANSFER.value

    def giveCoin(
        self,
        fromUserId: int,
        toUserId: int,
        amount: int,
        transactionType: str = TRANSACTION_TYPE,
        note: str = "User transfer chill coin",
        skipDailyReceiveLimit: bool = False,
    ):
        if amount is None or amount <= 0:
            return {
                "success": False,
                "message": "Số chill coin chuyển phải lớn hơn 0.",
            }

        if fromUserId == toUserId:
            return {
                "success": False,
                "message": "Bạn không thể tự chuyển chill coin cho chính mình.",
            }

        with getDbSession() as session:
            memberRepository = MemberRepository(session)
            chillCoinTransactionRepository = ChillCoinTransactionRepository(session)

            fromMember = memberRepository.findByUserId(fromUserId)

            if fromMember is None:
                return {
                    "success": False,
                    "message": "Không tìm thấy dữ liệu member của bạn.",
                }

            toMember = memberRepository.findByUserId(toUserId)

            if toMember is None:
                return {
                    "success": False,
                    "message": "Không tìm thấy dữ liệu member nhận chill coin.",
                }

            chillCoinEmoji = FARM_GAME_EMOJI["chill_coin"]

            if fromMember.chill_coin < amount:
                return {
                    "success": False,
                    "message": (
                        f"Bạn không đủ {chillCoinEmoji} để chuyển. "
                        f"Muốn chuyển **{formatNumber(amount)}** {chillCoinEmoji}, "
                        f"hiện có **{formatNumber(fromMember.chill_coin)}** {chillCoinEmoji}."
                    ),
                }

            if not skipDailyReceiveLimit:
                startAt, endAt = self.getTodayRange()
                receivedTodayAmount = chillCoinTransactionRepository.sumReceivedAmountByUserIdBetween(
                    userId=toUserId,
                    startAt=startAt,
                    endAt=endAt,
                    transactionType=self.TRANSACTION_TYPE,
                )

                remainingReceivableAmount = self.DAILY_RECEIVE_LIMIT - receivedTodayAmount

                if remainingReceivableAmount <= 0:
                    return {
                        "success": False,
                        "message": (
                            f"Hôm nay người này đã nhận đủ giới hạn "
                            f"**{formatNumber(self.DAILY_RECEIVE_LIMIT)}** {chillCoinEmoji} rồi."
                        ),
                    }

                if amount > remainingReceivableAmount:
                    return {
                        "success": False,
                        "message": (
                            f"Hôm nay người này chỉ nhận thêm được "
                            f"**{formatNumber(remainingReceivableAmount)}** {chillCoinEmoji} nữa thôi."
                        ),
                    }

            fromMember.chill_coin -= amount
            toMember.chill_coin += amount

            chillCoinTransactionRepository.create(
                fromUserId=fromUserId,
                toUserId=toUserId,
                amount=amount,
                transactionType=transactionType,
                note=note,
            )

            session.commit()

            return {
                "success": True,
                "message": (
                    f"Bạn đã chuyển **{formatNumber(amount)}** {chillCoinEmoji} "
                    f"cho **{self.getMemberDisplayName(toMember)}**."
                ),
            }

    def getTodayRange(self):
        now = datetime.now()
        startAt = datetime.combine(now.date(), time.min)
        endAt = startAt + timedelta(days=1)

        return startAt, endAt

    def getMemberDisplayName(self, member):
        if member.nick:
            return member.nick

        if member.global_name:
            return member.global_name

        return member.username
