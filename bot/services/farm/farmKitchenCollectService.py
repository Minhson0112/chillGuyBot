from datetime import datetime

from bot.config.database import getDbSession
from bot.helper.timeFormatHelper import formatMinutesSeconds
from bot.helper.farmItemHelper import buildItemText
from bot.repository.farmKitchenRepository import FarmKitchenRepository
from bot.repository.farmRepository import FarmRepository
from bot.repository.userInventoryRepository import UserInventoryRepository


class FarmKitchenCollectService:
    def collectFood(self, userId: int):
        with getDbSession() as session:
            farmRepository = FarmRepository(session)
            farmKitchenRepository = FarmKitchenRepository(session)
            userInventoryRepository = UserInventoryRepository(session)

            farm = farmRepository.findByUserId(userId)

            if farm is None:
                return {
                    "success": False,
                    "message": "Bạn chưa có nông trại.",
                }

            farmKitchen = farmKitchenRepository.findByFarmIdWithCurrentRecipe(farm.id)

            if farmKitchen is None:
                return {
                    "success": False,
                    "message": "Nông trại của bạn chưa có nhà bếp.",
                }

            if farmKitchen.current_recipe_id is None or farmKitchen.cooking_quantity <= 0:
                return {
                    "success": False,
                    "message": "Nhà bếp hiện không có món nào để nhận.",
                }

            recipe = farmKitchen.currentRecipe

            if recipe is None or recipe.resultItem is None:
                return {
                    "success": False,
                    "message": "Dữ liệu món đang nấu không hợp lệ.",
                }

            if farmKitchen.finished_at is None:
                return {
                    "success": False,
                    "message": "Dữ liệu thời gian nấu không hợp lệ.",
                }

            now = datetime.now()

            if now < farmKitchen.finished_at:
                remainingSeconds = int((farmKitchen.finished_at - now).total_seconds())

                return {
                    "success": False,
                    "message": f"Món ăn chưa nấu xong. Còn **{formatMinutesSeconds(remainingSeconds)}**.",
                }

            resultQuantity = recipe.result_quantity * farmKitchen.cooking_quantity
            resultItem = recipe.resultItem

            userInventoryRepository.addOrCreate(
                userId=userId,
                itemId=resultItem.id,
                quantity=resultQuantity,
            )

            farmKitchenRepository.resetKitchen(farmKitchen)

            session.commit()

            return {
                "success": True,
                "message": f"Bạn đã nhận **{resultQuantity}** {buildItemText(resultItem)}.",
            }
