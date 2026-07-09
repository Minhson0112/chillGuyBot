from sqlalchemy import asc
from sqlalchemy.orm import selectinload

from bot.models.farmAchievementCategory import FarmAchievementCategory
from bot.models.farmAchievementMaster import FarmAchievementMaster


class FarmAchievementCategoryRepository:
    def __init__(self, session):
        self.session = session

    def findActiveCategoriesWithAchievements(self):
        return (
            self.session.query(FarmAchievementCategory)
            .options(
                selectinload(FarmAchievementCategory.achievements)
                .joinedload(FarmAchievementMaster.targetItem),
                selectinload(FarmAchievementCategory.achievements)
                .selectinload(FarmAchievementMaster.rewards),
            )
            .filter(FarmAchievementCategory.is_active.is_(True))
            .order_by(
                asc(FarmAchievementCategory.sort_order),
                asc(FarmAchievementCategory.id),
            )
            .all()
        )
