from datetime import datetime

from bot.config.database import getDbSession
from bot.repository.farmCropAreaRepository import FarmCropAreaRepository
from bot.repository.farmRepository import FarmRepository


class FarmWaterService:
    WATER_EXP = 1
    def waterCrop(self, userId: int):
        with getDbSession() as session:
            farmRepository = FarmRepository(session)
            farmCropAreaRepository = FarmCropAreaRepository(session)

            farm = farmRepository.findByUserId(userId)

            if farm is None:
                return {
                    "success": False,
                    "message": "Bạn chưa có nông trại.",
                }

            farmCropArea = farmCropAreaRepository.findByFarmId(farm.id)

            if farmCropArea is None:
                return {
                    "success": False,
                    "message": "Nông trại của bạn chưa có khu đất trồng.",
                }

            if farmCropArea.crop_id is None or farmCropArea.planted_at is None:
                return {
                    "success": False,
                    "message": "Bạn chưa trồng cây nào để tưới nước.",
                }

            if farmCropArea.harvestable_at is not None and datetime.now() >= farmCropArea.harvestable_at:
                return {
                    "success": False,
                    "message": "Cây đã có thể thu hoạch rồi, không cần tưới nước nữa.",
                }

            if not farmCropArea.is_dry:
                return {
                    "success": False,
                    "message": "Đất vẫn đang ướt, chưa cần tưới nước.",
                }

            farmCropAreaRepository.markWatered(farmCropArea)
            farmRepository.increaseFarmExp(farm, self.WATER_EXP)

            session.commit()

            return {
                "success": True,
                "message": "Bạn đã tưới nước cho cây. Đất đã ướt trở lại.",
            }