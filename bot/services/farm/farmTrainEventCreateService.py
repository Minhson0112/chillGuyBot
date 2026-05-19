from bot.config.database import getDbSession
from bot.config.emoji import FARM_GAME_EMOJI
from bot.repository.farmRepository import FarmRepository
from bot.repository.farmTrainEventRepository import FarmTrainEventRepository
from bot.repository.itemRepository import ItemRepository


class FarmTrainEventCreateService:
    def createTrainEvent(
        self,
        requiredItemId: int,
        requiredQuantity: int,
        rewardChillCoin: int,
        rewardExp: int,
        createdByUserId: int,
    ):
        if requiredQuantity <= 0:
            return {
                "success": False,
                "message": "Số lượng item yêu cầu phải lớn hơn 0.",
            }

        if rewardChillCoin < 0:
            return {
                "success": False,
                "message": "Chill coin thưởng không được nhỏ hơn 0.",
            }

        if rewardExp < 0:
            return {
                "success": False,
                "message": "EXP thưởng không được nhỏ hơn 0.",
            }

        with getDbSession() as session:
            itemRepository = ItemRepository(session)
            farmRepository = FarmRepository(session)
            farmTrainEventRepository = FarmTrainEventRepository(session)

            item = itemRepository.findById(requiredItemId)

            if item is None:
                return {
                    "success": False,
                    "message": f"Không tìm thấy item với ID **{requiredItemId}**.",
                }

            farmTrainEvent = farmTrainEventRepository.create(
                requiredItemId=requiredItemId,
                requiredQuantity=requiredQuantity,
                rewardChillCoin=rewardChillCoin,
                rewardExp=rewardExp,
                createdByUserId=createdByUserId,
            )

            farmRepository.updateAllTrainEventFlag(True)

            session.commit()

            chillCoinEmoji = FARM_GAME_EMOJI["chill_coin"]
            itemText = self.buildItemText(item)

            return {
                "success": True,
                "message": (
                    f"Đã tạo sự kiện tàu hỏa **#{farmTrainEvent.id}**.\n"
                    f"Yêu cầu: **{self.formatNumber(requiredQuantity)}** {itemText}\n"
                    f"Thưởng: **{self.formatNumber(rewardChillCoin)}** {chillCoinEmoji}"
                    f"và **{self.formatNumber(rewardExp)} EXP**.\n"
                    f"Tàu hỏa đã xuất hiện ở toàn bộ farm."
                ),
            }

    def buildItemText(self, item):
        itemEmoji = FARM_GAME_EMOJI.get(item.icon_image_key)

        if itemEmoji is None:
            return f"**{item.name}**"

        return f"{itemEmoji} **{item.name}**"

    def formatNumber(self, number: int):
        return f"{number:,}"