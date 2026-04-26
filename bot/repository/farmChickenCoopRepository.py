from bot.models.farmChickenCoop import FarmChickenCoop


class FarmChickenCoopRepository:
    def __init__(self, session):
        self.session = session

    def findByFarmId(self, farmId: int):
        return (
            self.session.query(FarmChickenCoop)
            .filter(FarmChickenCoop.farm_id == farmId)
            .first()
        )

    def createDefaultChickenCoop(self, farmId: int):
        farmChickenCoop = FarmChickenCoop(
            farm_id=farmId,
            chicken_count=0,
            render_scale=1.0,
        )

        self.session.add(farmChickenCoop)
        self.session.flush()

        return farmChickenCoop