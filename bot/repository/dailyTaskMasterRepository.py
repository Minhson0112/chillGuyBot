from sqlalchemy import asc
from sqlalchemy.orm import joinedload

from bot.models.dailyTaskMaster import DailyTaskMaster


class DailyTaskMasterRepository:
    def __init__(self, session):
        self.session = session

    def findActiveTasksByFarmLevel(self, farmLevel: int):
        return (
            self.session.query(DailyTaskMaster)
            .options(
                joinedload(DailyTaskMaster.targetItem),
                joinedload(DailyTaskMaster.targetCrop),
            )
            .filter(DailyTaskMaster.is_active.is_(True))
            .filter(DailyTaskMaster.min_farm_level <= farmLevel)
            .order_by(asc(DailyTaskMaster.id))
            .all()
        )