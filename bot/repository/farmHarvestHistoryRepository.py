from bot.models.farmHarvestHistory import FarmHarvestHistory


class FarmHarvestHistoryRepository:
    def __init__(self, session):
        self.session = session

    def create(
        self,
        userId: int,
        itemId: int,
        quantity: int,
        isPerfectHarvest: bool,
        harvestedAt,
    ):
        farmHarvestHistory = FarmHarvestHistory(
            user_id=userId,
            item_id=itemId,
            quantity=quantity,
            is_perfect_harvest=isPerfectHarvest,
            harvested_at=harvestedAt,
        )

        self.session.add(farmHarvestHistory)
        self.session.flush()

        return farmHarvestHistory
