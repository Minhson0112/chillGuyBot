from bot.models.giftcodeClaimHistory import GiftcodeClaimHistory


class GiftcodeClaimHistoryRepository:
    def __init__(self, session):
        self.session = session

    def findByUserIdAndGiftcodeId(
        self,
        userId: int,
        giftcodeId: int,
    ):
        return (
            self.session.query(GiftcodeClaimHistory)
            .filter(GiftcodeClaimHistory.user_id == userId)
            .filter(GiftcodeClaimHistory.giftcode_id == giftcodeId)
            .first()
        )

    def create(
        self,
        userId: int,
        giftcodeId: int,
    ):
        giftcodeClaimHistory = GiftcodeClaimHistory(
            user_id=userId,
            giftcode_id=giftcodeId,
        )

        self.session.add(giftcodeClaimHistory)
        self.session.flush()

        return giftcodeClaimHistory