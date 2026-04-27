from bot.models.farmCowShed import FarmCowShed
from datetime import datetime


class FarmCowShedRepository:
    def __init__(self, session):
        self.session = session

    def findByFarmId(self, farmId: int):
        return (
            self.session.query(FarmCowShed)
            .filter(FarmCowShed.farm_id == farmId)
            .first()
        )

    def createDefaultCowShed(self, farmId: int):
        farmCowShed = FarmCowShed(
            farm_id=farmId,
            cow_count=0,
            render_scale=1.0,
        )

        self.session.add(farmCowShed)
        self.session.flush()

        return farmCowShed
    
    def increaseCowCount(self, farmCowShed: FarmCowShed):
        farmCowShed.cow_count += 1

        if farmCowShed.cow_count == 1:
            farmCowShed.cow_x = 180
            farmCowShed.cow_y = 220
        
        farmCowShed.last_collected_milk_at = datetime.now()

        self.session.flush()

        return farmCowShed