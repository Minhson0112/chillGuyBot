from bot.models.farmMilkHarvestHistory import FarmMilkHarvestHistory


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
