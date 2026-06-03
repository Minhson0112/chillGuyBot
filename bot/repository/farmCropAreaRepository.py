from datetime import datetime, timedelta
from sqlalchemy import and_, or_
from sqlalchemy.orm import joinedload

from bot.models.crop import Crop
from bot.models.farm import Farm
from bot.models.farmCropArea import FarmCropArea


class FarmCropAreaRepository:
    def __init__(self, session):
        self.session = session

    def findById(self, farmCropAreaId: int):
        return (
            self.session.query(FarmCropArea)
            .filter(FarmCropArea.id == farmCropAreaId)
            .first()
        )

    def findByFarmId(self, farmId: int):
        return (
            self.session.query(FarmCropArea)
            .filter(FarmCropArea.farm_id == farmId)
            .first()
        )

    def createDefaultCropArea(
        self,
        farmId: int,
        unlockedPlotCount: int = 16,
    ):
        farmCropArea = FarmCropArea(
            farm_id=farmId,
            unlocked_plot_count=unlockedPlotCount,
            status="idle",
        )

        self.session.add(farmCropArea)
        self.session.flush()

        return farmCropArea

    def plantCrop(
        self,
        farmCropArea: FarmCropArea,
        cropId: int,
        totalGrowthSeconds: int,
    ):
        now = datetime.now()

        farmCropArea.crop_id = cropId
        farmCropArea.planted_at = now
        farmCropArea.harvestable_at = now + timedelta(seconds=totalGrowthSeconds)

        farmCropArea.last_watered_at = None
        farmCropArea.last_pest_removed_at = None

        farmCropArea.is_dry = False
        farmCropArea.is_pest_infected = False

        farmCropArea.dryness_started_at = None
        farmCropArea.pest_started_at = None

        farmCropArea.total_dry_seconds = 0
        farmCropArea.total_pest_seconds = 0

        farmCropArea.status = "planted"

        self.session.flush()

        return farmCropArea

    def clearCrop(self, farmCropArea: FarmCropArea):
        farmCropArea.crop_id = None
        farmCropArea.planted_at = None
        farmCropArea.harvestable_at = None

        farmCropArea.last_watered_at = None
        farmCropArea.last_pest_removed_at = None

        farmCropArea.is_dry = False
        farmCropArea.is_pest_infected = False

        farmCropArea.dryness_started_at = None
        farmCropArea.pest_started_at = None

        farmCropArea.total_dry_seconds = 0
        farmCropArea.total_pest_seconds = 0

        farmCropArea.status = "idle"

        self.session.flush()

        return farmCropArea

    def markDry(self, farmCropArea: FarmCropArea):
        if farmCropArea.is_dry:
            return farmCropArea

        farmCropArea.is_dry = True
        farmCropArea.dryness_started_at = datetime.now()

        self.session.flush()

        return farmCropArea

    def markWatered(self, farmCropArea: FarmCropArea):
        now = datetime.now()

        if farmCropArea.is_dry and farmCropArea.dryness_started_at is not None:
            drySeconds = int((now - farmCropArea.dryness_started_at).total_seconds())
            farmCropArea.total_dry_seconds += max(drySeconds, 0)

        farmCropArea.is_dry = False
        farmCropArea.dryness_started_at = None
        farmCropArea.last_watered_at = now

        self.session.flush()

        return farmCropArea

    def markPestInfected(self, farmCropArea: FarmCropArea):
        if farmCropArea.is_pest_infected:
            return farmCropArea

        farmCropArea.is_pest_infected = True
        farmCropArea.pest_started_at = datetime.now()

        self.session.flush()

        return farmCropArea

    def markPestRemoved(self, farmCropArea: FarmCropArea):
        now = datetime.now()

        if farmCropArea.is_pest_infected and farmCropArea.pest_started_at is not None:
            pestSeconds = int((now - farmCropArea.pest_started_at).total_seconds())
            farmCropArea.total_pest_seconds += max(pestSeconds, 0)

        farmCropArea.is_pest_infected = False
        farmCropArea.pest_started_at = None
        farmCropArea.last_pest_removed_at = now

        self.session.flush()

        return farmCropArea

    def findCropAreasNeedDry(self, now: datetime, dryThresholdMinutes: int):
        thresholdAt = now - timedelta(minutes=dryThresholdMinutes)

        return (
            self.session.query(FarmCropArea)
            .options(
                joinedload(FarmCropArea.farm).joinedload(Farm.member),
            )
            .filter(FarmCropArea.crop_id.isnot(None))
            .filter(FarmCropArea.planted_at.isnot(None))
            .filter(FarmCropArea.harvestable_at > now)
            .filter(FarmCropArea.is_dry.is_(False))
            .filter(
                or_(
                    FarmCropArea.last_watered_at <= thresholdAt,
                    and_(
                        FarmCropArea.last_watered_at.is_(None),
                        FarmCropArea.planted_at <= thresholdAt,
                    ),
                )
            )
            .all()
        )

    def findCropAreasNeedPestInfected(self, now: datetime, pestThresholdMinutes: int):
        thresholdAt = now - timedelta(minutes=pestThresholdMinutes)

        return (
            self.session.query(FarmCropArea)
            .options(
                joinedload(FarmCropArea.farm).joinedload(Farm.member),
            )
            .filter(FarmCropArea.crop_id.isnot(None))
            .filter(FarmCropArea.planted_at.isnot(None))
            .filter(FarmCropArea.harvestable_at > now)
            .filter(FarmCropArea.is_pest_infected.is_(False))
            .filter(
                or_(
                    FarmCropArea.last_pest_removed_at <= thresholdAt,
                    and_(
                        FarmCropArea.last_pest_removed_at.is_(None),
                        FarmCropArea.planted_at <= thresholdAt,
                    ),
                )
            )
            .all()
        )

    def findHarvestableCropAreasNeedNotification(self, now: datetime):
        return (
            self.session.query(FarmCropArea)
            .options(
                joinedload(FarmCropArea.farm).joinedload(Farm.member),
                joinedload(FarmCropArea.crop).joinedload(Crop.cropItem),
            )
            .filter(FarmCropArea.crop_id.isnot(None))
            .filter(FarmCropArea.planted_at.isnot(None))
            .filter(FarmCropArea.harvestable_at <= now)
            .filter(FarmCropArea.status == "planted")
            .all()
        )

    def markHarvestReadyNotified(self, farmCropArea: FarmCropArea):
        farmCropArea.status = "harvest_ready_notified"

        self.session.flush()

        return farmCropArea
    
    def increaseUnlockedPlotCount(self, farmCropArea):
        farmCropArea.unlocked_plot_count += 1

        self.session.flush()

        return farmCropArea
    
    def reduceGrowthTime(
        self,
        farmCropArea: FarmCropArea,
        reductionSeconds: int,
    ):
        if reductionSeconds <= 0:
            return farmCropArea

        if farmCropArea.planted_at is not None:
            farmCropArea.planted_at -= timedelta(seconds=reductionSeconds)

        if farmCropArea.harvestable_at is not None:
            farmCropArea.harvestable_at -= timedelta(seconds=reductionSeconds)

        self.session.flush()

        return farmCropArea
