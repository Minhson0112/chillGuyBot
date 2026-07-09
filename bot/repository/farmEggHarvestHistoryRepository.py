from bot.models.farmEggHarvestHistory import FarmEggHarvestHistory
from sqlalchemy import func


class FarmEggHarvestHistoryRepository:
    def __init__(self, session):
        self.session = session

    def create(
        self,
        userId: int,
        itemId: int,
        quantity: int,
        harvestedAt,
    ):
        farmEggHarvestHistory = FarmEggHarvestHistory(
            user_id=userId,
            item_id=itemId,
            quantity=quantity,
            harvested_at=harvestedAt,
        )

        self.session.add(farmEggHarvestHistory)
        self.session.flush()

        return farmEggHarvestHistory

    def sumQuantityByUserIdAndItemId(
        self,
        userId: int,
        itemId: int,
    ):
        return (
            self.session.query(func.coalesce(func.sum(FarmEggHarvestHistory.quantity), 0))
            .filter(FarmEggHarvestHistory.user_id == userId)
            .filter(FarmEggHarvestHistory.item_id == itemId)
            .scalar()
            or 0
        )
