from sqlalchemy import and_, func, or_

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

    def countGiftHistoriesBetweenUsers(self, user1Id: int, user2Id: int):
        return (
            self.session.query(func.count(ServerItemGiftHistory.id))
            .filter(
                or_(
                    and_(
                        ServerItemGiftHistory.giver_user_id == user1Id,
                        ServerItemGiftHistory.receiver_user_id == user2Id,
                    ),
                    and_(
                        ServerItemGiftHistory.giver_user_id == user2Id,
                        ServerItemGiftHistory.receiver_user_id == user1Id,
                    ),
                ),
            )
            .scalar()
            or 0
        )
