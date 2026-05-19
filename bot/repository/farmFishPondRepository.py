from bot.models.farmFishPond import FarmFishPond
from datetime import datetime


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
    
    def markFished(self, farmFishPond: FarmFishPond):
        farmFishPond.last_fished_at = datetime.now()

        self.session.flush()

        return farmFishPond