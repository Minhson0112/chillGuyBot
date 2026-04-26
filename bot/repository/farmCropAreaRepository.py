from datetime import datetime, timedelta

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