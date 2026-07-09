from bot.models.farmMilkHarvestHistory import FarmMilkHarvestHistory
from sqlalchemy import func


class FarmMilkHarvestHistoryRepository:
    def __init__(self, session):
        self.session = session

    def create(
        self,
        userId: int,
        itemId: int,
        quantity: int,
        harvestedAt,
    ):
        farmMilkHarvestHistory = FarmMilkHarvestHistory(
            user_id=userId,
            item_id=itemId,
            quantity=quantity,
            harvested_at=harvestedAt,
        )

        self.session.add(farmMilkHarvestHistory)
        self.session.flush()

        return farmMilkHarvestHistory

    def sumQuantityByUserIdAndItemId(
        self,
        userId: int,
        itemId: int,
    ):
        return (
            self.session.query(func.coalesce(func.sum(FarmMilkHarvestHistory.quantity), 0))
            .filter(FarmMilkHarvestHistory.user_id == userId)
            .filter(FarmMilkHarvestHistory.item_id == itemId)
            .scalar()
            or 0
        )
