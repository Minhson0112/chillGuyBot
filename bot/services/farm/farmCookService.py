from datetime import datetime, timedelta

from bot.config.database import getDbSession
from bot.config.emoji import FARM_GAME_EMOJI
from bot.repository.farmKitchenRepository import FarmKitchenRepository
from bot.repository.farmRepository import FarmRepository
from bot.repository.foodRecipeRepository import FoodRecipeRepository
from bot.repository.userInventoryRepository import UserInventoryRepository


class FarmCookService:
    def cook(
        self,
        userId: int,
        resultItemId: int,
        cookingQuantity: int = 1,
    ):
        if cookingQuantity is None:
            cookingQuantity = 1

        if cookingQuantity <= 0:
            return {
                "success": False,
                "message": "Số lượng muốn nấu phải lớn hơn 0.",
            }

        with getDbSession() as session:
            farmRepository = FarmRepository(session)
            farmKitchenRepository = FarmKitchenRepository(session)
            foodRecipeRepository = FoodRecipeRepository(session)
            userInventoryRepository = UserInventoryRepository(session)

            farm = farmRepository.findByUserId(userId)

            if farm is None:
                return {
                    "success": False,
                    "message": "Bạn chưa có nông trại.",
                }

            farmKitchen = farmKitchenRepository.findByFarmId(farm.id)

            if farmKitchen is None:
                return {
                    "success": False,
                    "message": "Nông trại của bạn chưa có nhà bếp.",
                }

            if not self.isKitchenIdle(farmKitchen):
                return {
                    "success": False,
                    "message": self.buildKitchenBusyMessage(farmKitchen),
                }

            recipe = foodRecipeRepository.findByResultItemIdWithIngredients(resultItemId)

            if recipe is None or recipe.resultItem is None:
                return {
                    "success": False,
                    "message": f"Không tìm thấy công thức nấu ăn với item ID **{resultItemId}**.",
                }

            if not recipe.is_active:
                return {
                    "success": False,
                    "message": "Công thức này hiện không thể nấu.",
                }

            if farm.farm_level < recipe.required_farm_level:
                return {
                    "success": False,
                    "message": (
                        f"Món này yêu cầu farm level **{recipe.required_farm_level}**, "
                        f"farm của bạn hiện level **{farm.farm_level}**."
                    ),
                }

            missingIngredientMessages = self.validateIngredients(
                userInventoryRepository=userInventoryRepository,
                userId=userId,
                recipe=recipe,
                cookingQuantity=cookingQuantity,
            )

            if missingIngredientMessages:
                return {
                    "success": False,
                    "message": (
                        "Bạn không đủ nguyên liệu để nấu món này:\n"
                        + "\n".join(missingIngredientMessages)
                    ),
                }

            self.consumeIngredients(
                userInventoryRepository=userInventoryRepository,
                userId=userId,
                recipe=recipe,
                cookingQuantity=cookingQuantity,
            )

            now = datetime.now()
            totalCookingSeconds = recipe.cooking_seconds * cookingQuantity
            finishedAt = now + timedelta(seconds=totalCookingSeconds)

            farmKitchenRepository.startCooking(
                farmKitchen=farmKitchen,
                recipeId=recipe.id,
                cookingQuantity=cookingQuantity,
                startedAt=now,
                finishedAt=finishedAt,
                totalCookingSeconds=totalCookingSeconds,
            )

            session.commit()

            resultItemText = self.buildItemText(recipe.resultItem)

            return {
                "success": True,
                "message": (
                    f"Bạn đã bắt đầu nấu **{cookingQuantity}** {resultItemText}. "
                    f"Thời gian nấu: **{self.formatRemainingTime(totalCookingSeconds)}**."
                ),
            }

    def isKitchenIdle(self, farmKitchen):
        if farmKitchen.status != "idle":
            return False

        if farmKitchen.current_recipe_id is not None:
            return False

        return True

    def buildKitchenBusyMessage(self, farmKitchen):
        now = datetime.now()

        if farmKitchen.finished_at is not None:
            remainingSeconds = int((farmKitchen.finished_at - now).total_seconds())

            if remainingSeconds > 0:
                return f"Nhà bếp đang nấu món khác. Còn **{self.formatRemainingTime(remainingSeconds)}**."

            return "Món trong bếp đã nấu xong. Hãy nhận món trước khi nấu món mới."

        return "Nhà bếp đang bận, chưa thể nấu món mới."

    def validateIngredients(
        self,
        userInventoryRepository,
        userId: int,
        recipe,
        cookingQuantity: int,
    ):
        missingIngredientMessages = []

        for ingredient in recipe.ingredients:
            item = ingredient.item

            if item is None:
                continue

            requiredQuantity = ingredient.quantity * cookingQuantity

            inventory = userInventoryRepository.findByUserIdAndItemId(
                userId=userId,
                itemId=item.id,
            )

            currentQuantity = inventory.quantity if inventory is not None else 0

            if currentQuantity < requiredQuantity:
                missingIngredientMessages.append(
                    f"- {self.buildItemText(item)} cần **{requiredQuantity}**, hiện có **{currentQuantity}**."
                )

        return missingIngredientMessages

    def consumeIngredients(
        self,
        userInventoryRepository,
        userId: int,
        recipe,
        cookingQuantity: int,
    ):
        for ingredient in recipe.ingredients:
            item = ingredient.item

            if item is None:
                continue

            requiredQuantity = ingredient.quantity * cookingQuantity

            inventory = userInventoryRepository.findByUserIdAndItemId(
                userId=userId,
                itemId=item.id,
            )

            userInventoryRepository.decreaseQuantity(
                userInventory=inventory,
                quantity=requiredQuantity,
            )

    def buildItemText(self, item):
        itemEmoji = FARM_GAME_EMOJI.get(item.icon_image_key)

        if itemEmoji is None:
            return f"**{item.name}**"

        return f"{itemEmoji} **{item.name}**"

    def formatRemainingTime(self, remainingSeconds: int):
        minutes = remainingSeconds // 60
        seconds = remainingSeconds % 60

        return f"{minutes}:{seconds:02d}"