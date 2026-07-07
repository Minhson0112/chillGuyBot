from bot.models.serverItemGiftHistory import ServerItemGiftHistory


class ServerItemGiftHistoryRepository:
    def __init__(self, session):
        self.session = session

    def create(
        self,
        giverUserId: int,
        receiverUserId: int,
        itemId: int,
        quantity: int,
    ):
        serverItemGiftHistory = ServerItemGiftHistory(
            giver_user_id=giverUserId,
            receiver_user_id=receiverUserId,
            item_id=itemId,
            quantity=quantity,
        )

        self.session.add(serverItemGiftHistory)
        self.session.flush()
        return serverItemGiftHistory
