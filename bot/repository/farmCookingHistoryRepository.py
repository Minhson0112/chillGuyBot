from bot.models.farmCookingHistory import FarmCookingHistory


class FarmCookingHistoryRepository:
    def __init__(self, session):
        self.session = session

    def create(
        self,
        userId: int,
        itemId: int,
        quantity: int,
    ):
        farmCookingHistory = FarmCookingHistory(
            user_id=userId,
            item_id=itemId,
            quantity=quantity,
        )

        self.session.add(farmCookingHistory)
        self.session.flush()

        return farmCookingHistory
