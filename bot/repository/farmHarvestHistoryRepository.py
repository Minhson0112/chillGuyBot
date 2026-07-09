from sqlalchemy import func

from bot.models.crop import Crop
from bot.models.farmHarvestHistory import FarmHarvestHistory
from bot.models.shopItem import ShopItem


class FarmHarvestHistoryRepository:
    def __init__(self, session):
        self.session = session

    def create(
        self,
        userId: int,
        itemId: int,
        quantity: int,
        isPerfectHarvest: bool,
        harvestedAt,
    ):
        farmHarvestHistory = FarmHarvestHistory(
            user_id=userId,
            item_id=itemId,
            quantity=quantity,
            is_perfect_harvest=isPerfectHarvest,
            harvested_at=harvestedAt,
        )

        self.session.add(farmHarvestHistory)
        self.session.flush()

        return farmHarvestHistory

    def countRequiredCropsBySeedLevel(
        self,
        level: int,
    ):
        return (
            self.session.query(func.count(Crop.id))
            .join(ShopItem, ShopItem.item_id == Crop.seed_item_id)
            .filter(ShopItem.required_farm_level == level)
            .filter(ShopItem.is_active.is_(True))
            .scalar()
            or 0
        )

    def countDistinctHarvestedCropsByUserIdAndSeedLevel(
        self,
        userId: int,
        level: int,
    ):
        return (
            self.session.query(func.count(func.distinct(Crop.id)))
            .join(ShopItem, ShopItem.item_id == Crop.seed_item_id)
            .join(FarmHarvestHistory, FarmHarvestHistory.item_id == Crop.crop_item_id)
            .filter(ShopItem.required_farm_level == level)
            .filter(ShopItem.is_active.is_(True))
            .filter(FarmHarvestHistory.user_id == userId)
            .scalar()
            or 0
        )
