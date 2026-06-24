from bot.models.farmCowShed import FarmCowShed
from datetime import datetime
from datetime import timedelta
from sqlalchemy import and_, or_
from sqlalchemy.orm import joinedload

from bot.models.farm import Farm


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
            render_scale=2.0,
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
        farmCowShed.is_milk_ready_notified = False

        self.session.flush()

        return farmCowShed
    
    def markFed(self, farmCowShed: FarmCowShed):
        farmCowShed.last_fed_at = datetime.now()

        self.session.flush()

        return farmCowShed
    
    def markMilkCollected(self, farmCowShed: FarmCowShed):
        farmCowShed.last_collected_milk_at = datetime.now()
        farmCowShed.is_milk_ready_notified = False

        self.session.flush()

        return farmCowShed

    def findMilkReadyShedsNeedNotification(
        self,
        now: datetime,
        milkCollectIntervalMinutes: int,
        hungryIntervalMinutes: int,
    ):
        collectableThresholdAt = now - timedelta(minutes=milkCollectIntervalMinutes)
        hungryThresholdAt = now - timedelta(minutes=hungryIntervalMinutes)

        return (
            self.session.query(FarmCowShed)
            .options(
                joinedload(FarmCowShed.farm).joinedload(Farm.member),
            )
            .filter(
                FarmCowShed.cow_count > 0,
                FarmCowShed.last_collected_milk_at <= collectableThresholdAt,
                FarmCowShed.last_fed_at > hungryThresholdAt,
                FarmCowShed.is_milk_ready_notified.is_(False),
            )
            .all()
        )

    def markMilkReadyNotified(self, farmCowShed: FarmCowShed):
        farmCowShed.is_milk_ready_notified = True
        self.session.flush()

        return farmCowShed
    
    def findStarvedCowSheds(self, now: datetime, starvationHours: int):
        thresholdAt = now - timedelta(hours=starvationHours)

        return (
            self.session.query(FarmCowShed)
            .options(
                joinedload(FarmCowShed.farm).joinedload(Farm.member),
            )
            .filter(FarmCowShed.cow_count > 0)
            .filter(
                or_(
                    FarmCowShed.last_fed_at <= thresholdAt,
                    and_(
                        FarmCowShed.last_fed_at.is_(None),
                        FarmCowShed.last_collected_milk_at <= thresholdAt,
                    ),
                    and_(
                        FarmCowShed.last_fed_at.is_(None),
                        FarmCowShed.last_collected_milk_at.is_(None),
                        FarmCowShed.created_at <= thresholdAt,
                    ),
                )
            )
            .all()
        )
    
    def clearCows(self, farmCowShed: FarmCowShed):
        farmCowShed.cow_count = 0
        farmCowShed.cow_image_key = None
        farmCowShed.cow_x = None
        farmCowShed.cow_y = None
        farmCowShed.last_fed_at = None
        farmCowShed.last_collected_milk_at = None
        farmCowShed.is_milk_ready_notified = False

        self.session.flush()

        return farmCowShed
