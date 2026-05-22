from bot.models.chillCoinExchangeCowoncyHistory import ChillCoinExchangeCowoncyHistory


class ChillCoinExchangeCowoncyHistoryRepository:
    def __init__(self, session):
        self.session = session

    def create(
        self,
        senderUserId: int,
        receiverUserId: int,
        chillCoinAmount: int,
        cowoncyAmount: int,
        transferredAt,
    ):
        history = ChillCoinExchangeCowoncyHistory(
            sender_user_id=senderUserId,
            receiver_user_id=receiverUserId,
            chill_coin_amount=chillCoinAmount,
            cowoncy_amount=cowoncyAmount,
            transferred_at=transferredAt,
        )

        self.session.add(history)
        self.session.flush()

        return history

    def findByReceiverUserIdTransferredAtFrom(
        self,
        receiverUserId: int,
        transferredAtFrom,
    ):
        return (
            self.session.query(ChillCoinExchangeCowoncyHistory)
            .filter(ChillCoinExchangeCowoncyHistory.receiver_user_id == receiverUserId)
            .filter(ChillCoinExchangeCowoncyHistory.transferred_at >= transferredAtFrom)
            .order_by(ChillCoinExchangeCowoncyHistory.transferred_at.asc())
            .all()
        )
