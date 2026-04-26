from bot.models.farmCowShed import FarmCowShed


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