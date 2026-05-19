from sqlalchemy.orm import joinedload

from bot.models.crop import Crop


class CropRepository:
    def __init__(self, session):
        self.session = session

    def findById(self, cropId: int):
        return (
            self.session.query(Crop)
            .filter(Crop.id == cropId)
            .first()
        )

    def findByCode(self, code: str):
        return (
            self.session.query(Crop)
            .filter(Crop.code == code)
            .first()
        )

    def findBySeedItemId(self, seedItemId: int):
        return (
            self.session.query(Crop)
            .filter(Crop.seed_item_id == seedItemId)
            .first()
        )

    def findBySeedItemIdWithItems(self, seedItemId: int):
        return (
            self.session.query(Crop)
            .options(
                joinedload(Crop.seedItem),
                joinedload(Crop.cropItem),
            )
            .filter(Crop.seed_item_id == seedItemId)
            .first()
        )

    def findByCropItemId(self, cropItemId: int):
        return (
            self.session.query(Crop)
            .filter(Crop.crop_item_id == cropItemId)
            .first()
        )