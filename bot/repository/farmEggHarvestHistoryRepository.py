from bot.models.farmEggHarvestHistory import FarmEggHarvestHistory


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
