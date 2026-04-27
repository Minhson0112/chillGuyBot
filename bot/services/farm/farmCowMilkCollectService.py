from datetime import datetime, timedelta

from bot.config.database import getDbSession
from bot.config.emoji import FARM_GAME_EMOJI
from bot.repository.farmCowShedRepository import FarmCowShedRepository
from bot.repository.farmRepository import FarmRepository
from bot.repository.itemRepository import ItemRepository
from bot.repository.userInventoryRepository import UserInventoryRepository


class FarmCowMilkCollectService:
    MILK_ITEM_CODE = "milk"
    HUNGRY_INTERVAL_MINUTES = 30
    MILK_COLLECT_INTERVAL_MINUTES = 15

    def collectMilk(self, userId: int):
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

            if self.isCowHungry(cowShed, now):
                return {
                    "success": False,
                    "message": "Bò đang đói. Bạn cần cho bò ăn rồi mới vắt được sữa.",
                }

            if not self.canCollectMilk(cowShed, now):
                remainingSeconds = self.calculateMilkCollectRemainingSeconds(cowShed, now)

                return {
                    "success": False,
                    "message": f"Chưa thể vắt sữa. Có thể vắt sau **{self.formatRemainingTime(remainingSeconds)}**.",
                }

            milkItem = itemRepository.findByCode(self.MILK_ITEM_CODE)

            if milkItem is None:
                return {
                    "success": False,
                    "message": "Không tìm thấy item sữa bò trong hệ thống.",
                }

            milkQuantity = cowShed.cow_count

            userInventoryRepository.addOrCreate(
                userId=userId,
                itemId=milkItem.id,
                quantity=milkQuantity,
            )

            farmCowShedRepository.markMilkCollected(cowShed)

            session.commit()

            milkText = self.buildItemText(milkItem)

            return {
                "success": True,
                "message": f"Bạn đã vắt được **{milkQuantity}** {milkText}.",
            }

    def isCowHungry(self, cowShed, now: datetime):
        if cowShed.last_fed_at is None:
            return True

        hungryAt = cowShed.last_fed_at + timedelta(minutes=self.HUNGRY_INTERVAL_MINUTES)

        return now >= hungryAt

    def canCollectMilk(self, cowShed, now: datetime):
        if cowShed.last_collected_milk_at is None:
            return True

        collectableAt = cowShed.last_collected_milk_at + timedelta(
            minutes=self.MILK_COLLECT_INTERVAL_MINUTES,
        )

        return now >= collectableAt

    def calculateMilkCollectRemainingSeconds(self, cowShed, now: datetime):
        collectableAt = cowShed.last_collected_milk_at + timedelta(
            minutes=self.MILK_COLLECT_INTERVAL_MINUTES,
        )
        remainingSeconds = int((collectableAt - now).total_seconds())

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