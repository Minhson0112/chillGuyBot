from bot.models.farmChickenCoop import FarmChickenCoop
from datetime import datetime
from datetime import timedelta
from sqlalchemy import and_, or_
from sqlalchemy.orm import joinedload

from bot.models.farm import Farm


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
            render_scale=2.0,
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
        
        farmChickenCoop.last_collected_egg_at = datetime.now()
        farmChickenCoop.is_egg_ready_notified = False

        self.session.flush()

        return farmChickenCoop
    
    def markFed(self, farmChickenCoop: FarmChickenCoop):
        farmChickenCoop.last_fed_at = datetime.now()
        self.session.flush()

        return farmChickenCoop
    
    def markEggCollected(self, farmChickenCoop: FarmChickenCoop):
        farmChickenCoop.last_collected_egg_at = datetime.now()
        farmChickenCoop.is_egg_ready_notified = False
        self.session.flush()

        return farmChickenCoop

    def findEggReadyCoopsNeedNotification(
        self,
        now: datetime,
        eggCollectIntervalMinutes: int,
        hungryIntervalMinutes: int,
    ):
        collectableThresholdAt = now - timedelta(minutes=eggCollectIntervalMinutes)
        hungryThresholdAt = now - timedelta(minutes=hungryIntervalMinutes)

        return (
            self.session.query(FarmChickenCoop)
            .options(
                joinedload(FarmChickenCoop.farm).joinedload(Farm.member),
            )
            .filter(
                FarmChickenCoop.chicken_count > 0,
                FarmChickenCoop.last_collected_egg_at <= collectableThresholdAt,
                FarmChickenCoop.last_fed_at > hungryThresholdAt,
                FarmChickenCoop.is_egg_ready_notified.is_(False),
            )
            .all()
        )

    def markEggReadyNotified(self, farmChickenCoop: FarmChickenCoop):
        farmChickenCoop.is_egg_ready_notified = True
        self.session.flush()

        return farmChickenCoop
    
    def findStarvedChickenCoops(self, now: datetime, starvationHours: int):
        thresholdAt = now - timedelta(hours=starvationHours)

        return (
            self.session.query(FarmChickenCoop)
            .options(
                joinedload(FarmChickenCoop.farm).joinedload(Farm.member),
            )
            .filter(FarmChickenCoop.chicken_count > 0)
            .filter(
                or_(
                    FarmChickenCoop.last_fed_at <= thresholdAt,
                    and_(
                        FarmChickenCoop.last_fed_at.is_(None),
                        FarmChickenCoop.last_collected_egg_at <= thresholdAt,
                    ),
                    and_(
                        FarmChickenCoop.last_fed_at.is_(None),
                        FarmChickenCoop.last_collected_egg_at.is_(None),
                        FarmChickenCoop.created_at <= thresholdAt,
                    ),
                )
            )
            .all()
        )
    
    def clearChickens(self, farmChickenCoop: FarmChickenCoop):
        farmChickenCoop.chicken_count = 0
        farmChickenCoop.chicken_1_x = None
        farmChickenCoop.chicken_1_y = None
        farmChickenCoop.chicken_2_x = None
        farmChickenCoop.chicken_2_y = None
        farmChickenCoop.last_fed_at = None
        farmChickenCoop.last_collected_egg_at = None
        farmChickenCoop.is_egg_ready_notified = False

        self.session.flush()

        return farmChickenCoop
