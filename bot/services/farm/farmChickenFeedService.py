from datetime import datetime, timedelta

from bot.config.database import getDbSession
from bot.helper.discordTimestampHelper import formatRelativeTime
from bot.helper.farmItemHelper import buildItemText
from bot.repository.farmChickenCoopRepository import FarmChickenCoopRepository
from bot.repository.farmRepository import FarmRepository
from bot.repository.itemRepository import ItemRepository
from bot.repository.userInventoryRepository import UserInventoryRepository


class FarmChickenFeedService:
    WHEAT_ITEM_CODE = "wheat"
    HUNGRY_INTERVAL_MINUTES = 30
    WHEAT_PER_CHICKEN = 1

    def feedChicken(self, userId: int):
        with getDbSession() as session:
            farmRepository = FarmRepository(session)
            farmChickenCoopRepository = FarmChickenCoopRepository(session)
            itemRepository = ItemRepository(session)
            userInventoryRepository = UserInventoryRepository(session)

            farm = farmRepository.findByUserId(userId)

            if farm is None:
                return {
                    "success": False,
                    "message": "Bạn chưa có nông trại.",
                }

            chickenCoop = farmChickenCoopRepository.findByFarmId(farm.id)

            if chickenCoop is None:
                return {
                    "success": False,
                    "message": "Nông trại của bạn chưa có chuồng gà.",
                }

            if chickenCoop.chicken_count <= 0:
                return {
                    "success": False,
                    "message": "Bạn chưa nuôi con gà nào.",
                }

            now = datetime.now()

            if not self.isChickenHungry(chickenCoop, now):
                hungryAt = self.getHungryAt(chickenCoop)

                return {
                    "success": False,
                    "message": f"Gà chưa đói. Có thể cho ăn sau **{formatRelativeTime(hungryAt)}**.",
                }

            wheatItem = itemRepository.findByCode(self.WHEAT_ITEM_CODE)

            if wheatItem is None:
                return {
                    "success": False,
                    "message": "Không tìm thấy item lúa mỳ trong hệ thống.",
                }

            requiredWheatQuantity = chickenCoop.chicken_count * self.WHEAT_PER_CHICKEN

            wheatInventory = userInventoryRepository.findByUserIdAndItemId(
                userId=userId,
                itemId=wheatItem.id,
            )

            wheatText = buildItemText(wheatItem)

            if wheatInventory is None or wheatInventory.quantity < requiredWheatQuantity:
                currentQuantity = wheatInventory.quantity if wheatInventory is not None else 0

                return {
                    "success": False,
                    "message": (
                        f"Không đủ {wheatText} để cho gà ăn. "
                        f"Bạn cần **{requiredWheatQuantity}** {wheatText}, "
                        f"hiện có **{currentQuantity}**."
                    ),
                }

            userInventoryRepository.decreaseQuantity(
                userInventory=wheatInventory,
                quantity=requiredWheatQuantity,
            )

            farmChickenCoopRepository.markFed(chickenCoop)

            session.commit()

            return {
                "success": True,
                "message": (
                    f"Bạn đã cho **{chickenCoop.chicken_count}** con gà ăn "
                    f"bằng **{requiredWheatQuantity}** {wheatText}."
                ),
            }

    def isChickenHungry(self, chickenCoop, now: datetime):
        if chickenCoop.last_fed_at is None:
            return True

        hungryAt = chickenCoop.last_fed_at + timedelta(minutes=self.HUNGRY_INTERVAL_MINUTES)

        return now >= hungryAt

    def getHungryAt(self, chickenCoop):
        return chickenCoop.last_fed_at + timedelta(minutes=self.HUNGRY_INTERVAL_MINUTES)
