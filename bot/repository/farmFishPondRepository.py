from bot.models.farmFishPond import FarmFishPond
from bot.models.farm import Farm
from datetime import datetime
from sqlalchemy.orm import joinedload


class FarmFishPondRepository:
    def __init__(self, session):
        self.session = session

    def findByFarmId(self, farmId: int):
        return (
            self.session.query(FarmFishPond)
            .filter(FarmFishPond.farm_id == farmId)
            .first()
        )

    def createDefaultFishPond(self, farmId: int):
        farmFishPond = FarmFishPond(
            farm_id=farmId,
        )

        self.session.add(farmFishPond)
        self.session.flush()

        return farmFishPond

    def markFished(
        self,
        farmFishPond: FarmFishPond,
        lastFishedAt: datetime,
        nextFishableAt: datetime,
    ):
        farmFishPond.last_fished_at = lastFishedAt
        farmFishPond.next_fishable_at = nextFishableAt
        farmFishPond.is_fishing_ready_notified = False

        self.session.flush()

        return farmFishPond

    def findFishingReadyPondsNeedNotification(self, now: datetime):
        return (
            self.session.query(FarmFishPond)
            .options(
                joinedload(FarmFishPond.farm).joinedload(Farm.member),
            )
            .filter(
                FarmFishPond.next_fishable_at.isnot(None),
                FarmFishPond.next_fishable_at <= now,
                FarmFishPond.is_fishing_ready_notified.is_(False),
            )
            .all()
        )

    def markFishingReadyNotified(self, farmFishPond: FarmFishPond):
        farmFishPond.is_fishing_ready_notified = True
        self.session.flush()

        return farmFishPond
