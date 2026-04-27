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
    
    def increaseChickenCount(self, farmChickenCoop: FarmChickenCoop):
        farmChickenCoop.chicken_count += 1

        if farmChickenCoop.chicken_count == 1:
            farmChickenCoop.chicken_1_x = 300
            farmChickenCoop.chicken_1_y = 470

        if farmChickenCoop.chicken_count == 2:
            farmChickenCoop.chicken_2_x = 200
            farmChickenCoop.chicken_2_y = 520

        self.session.flush()

        return farmChickenCoop