from bot.models.owoExchangeCoinHistory import OwoExchangeCoinHistory


class OwoExchangeCoinHistoryRepository:
    def __init__(self, session):
        self.session = session

    def create(
        self,
        messageId: int,
        channelId: int,
        senderUserId: int,
        receiverUserId: int,
        cowoncyAmount: int,
        transferredAt,
    ):
        owoExchangeCoinHistory = OwoExchangeCoinHistory(
            message_id=messageId,
            channel_id=channelId,
            sender_user_id=senderUserId,
            receiver_user_id=receiverUserId,
            cowoncy_amount=cowoncyAmount,
            transferred_at=transferredAt,
        )

        self.session.add(owoExchangeCoinHistory)
        self.session.flush()

        return owoExchangeCoinHistory

    def findByMessageId(self, messageId: int):
        return (
            self.session.query(OwoExchangeCoinHistory)
            .filter(OwoExchangeCoinHistory.message_id == messageId)
            .first()
        )

    def findBySenderUserIdTransferredAtFrom(
        self,
        senderUserId: int,
        transferredAtFrom,
    ):
        return (
            self.session.query(OwoExchangeCoinHistory)
            .filter(OwoExchangeCoinHistory.sender_user_id == senderUserId)
            .filter(OwoExchangeCoinHistory.transferred_at >= transferredAtFrom)
            .order_by(OwoExchangeCoinHistory.transferred_at.asc())
            .all()
        )
