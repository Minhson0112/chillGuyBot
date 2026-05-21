from datetime import datetime, timedelta

from bot.config.database import getDbSession
from bot.config.emoji import FARM_GAME_EMOJI
from bot.repository.farmCowShedRepository import FarmCowShedRepository
from bot.repository.farmRepository import FarmRepository
from bot.repository.itemRepository import ItemRepository
from bot.repository.userInventoryRepository import UserInventoryRepository


class FarmCowFeedService:
    WHEAT_ITEM_CODE = "wheat"
    HUNGRY_INTERVAL_MINUTES = 30
    WHEAT_PER_COW = 3

    def feedCow(self, userId: int):
        with getDbSession() as session:
            farmRepository = FarmRepository(session)
            farmCowShedRepository = FarmCowShedRepository(session)
            itemRepository = ItemRepository(session)
            userInventoryRepository = UserInventoryRepository(session)

            farm = farmRepository.findByUserId(userId)

            if farm is None:
                return {
                    "success": False,
                    "message": "Bạn chưa có nông trại.",
                }

            cowShed = farmCowShedRepository.findByFarmId(farm.id)

            if cowShed is None:
                return {
                    "success": False,
                    "message": "Nông trại của bạn chưa có chuồng bò.",
                }

            if cowShed.cow_count <= 0:
                return {
                    "success": False,
                    "message": "Bạn chưa nuôi con bò nào.",
                }

            now = datetime.now()

            if not self.isCowHungry(cowShed, now):
                remainingSeconds = self.calculateHungryRemainingSeconds(cowShed, now)

                return {
                    "success": False,
                    "message": f"Bò chưa đói. Có thể cho ăn sau **{self.formatRemainingTime(remainingSeconds)}**.",
                }

            wheatItem = itemRepository.findByCode(self.WHEAT_ITEM_CODE)

            if wheatItem is None:
                return {
                    "success": False,
                    "message": "Không tìm thấy item lúa mỳ trong hệ thống.",
                }

            requiredWheatQuantity = cowShed.cow_count * self.WHEAT_PER_COW

            wheatInventory = userInventoryRepository.findByUserIdAndItemId(
                userId=userId,
                itemId=wheatItem.id,
            )

            wheatText = self.buildItemText(wheatItem)

            if wheatInventory is None or wheatInventory.quantity < requiredWheatQuantity:
                currentQuantity = wheatInventory.quantity if wheatInventory is not None else 0

                return {
                    "success": False,
                    "message": (
                        f"Không đủ {wheatText} để cho bò ăn. "
                        f"Bạn cần **{requiredWheatQuantity}** {wheatText}, "
                        f"hiện có **{currentQuantity}**."
                    ),
                }

            userInventoryRepository.decreaseQuantity(
                userInventory=wheatInventory,
                quantity=requiredWheatQuantity,
            )

            farmCowShedRepository.markFed(cowShed)

            session.commit()

            return {
                "success": True,
                "message": (
                    f"Bạn đã cho **{cowShed.cow_count}** con bò ăn "
                    f"bằng **{requiredWheatQuantity}** {wheatText}."
                ),
            }

    def isCowHungry(self, cowShed, now: datetime):
        if cowShed.last_fed_at is None:
            return True

        hungryAt = cowShed.last_fed_at + timedelta(minutes=self.HUNGRY_INTERVAL_MINUTES)

        return now >= hungryAt

    def calculateHungryRemainingSeconds(self, cowShed, now: datetime):
        hungryAt = cowShed.last_fed_at + timedelta(minutes=self.HUNGRY_INTERVAL_MINUTES)
        remainingSeconds = int((hungryAt - now).total_seconds())

        return max(remainingSeconds, 0)

    def buildItemText(self, item):
        itemEmoji = FARM_GAME_EMOJI.get(item.icon_image_key)

        if itemEmoji is None:
            return f"**{item.name}**"

        return f"{itemEmoji} **{item.name}**"

    def formatRemainingTime(self, remainingSeconds: int):
        minutes = remainingSeconds // 60
        seconds = remainingSeconds % 60

        return f"{minutes}:{seconds:02d}"