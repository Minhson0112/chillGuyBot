from bot.models.farmTheftHistory import FarmTheftHistory


class FarmTheftHistoryRepository:
    def __init__(self, session):
        self.session = session

    def findLatestByThiefUserId(self, thiefUserId: int):
        return (
            self.session.query(FarmTheftHistory)
            .filter(FarmTheftHistory.thief_user_id == thiefUserId)
            .order_by(
                FarmTheftHistory.stolen_at.desc(),
                FarmTheftHistory.id.desc(),
            )
            .first()
        )

    def create(
        self,
        thiefUserId: int,
        victimUserId: int,
        itemId: int,
        stolenAt,
    ):
        farmTheftHistory = FarmTheftHistory(
            thief_user_id=thiefUserId,
            victim_user_id=victimUserId,
            item_id=itemId,
            stolen_at=stolenAt,
        )

        self.session.add(farmTheftHistory)
        self.session.flush()

        return farmTheftHistory
