from bot.config.database import getDbSession
from bot.config.emoji import FARM_GAME_EMOJI
from bot.repository.farmRepository import FarmRepository
from bot.repository.farmTrainEventHistoryRepository import FarmTrainEventHistoryRepository
from bot.repository.farmTrainEventRepository import FarmTrainEventRepository
from bot.repository.memberRepository import MemberRepository
from bot.repository.userInventoryRepository import UserInventoryRepository


class FarmTrainEventQueueService:
    def queueTrain(self, userId: int):
        with getDbSession() as session:
            farmRepository = FarmRepository(session)
            memberRepository = MemberRepository(session)
            farmTrainEventRepository = FarmTrainEventRepository(session)
            farmTrainEventHistoryRepository = FarmTrainEventHistoryRepository(session)
            userInventoryRepository = UserInventoryRepository(session)

            farm = farmRepository.findByUserId(userId)

            if farm is None:
                return {
                    "success": False,
                    "message": "Bạn chưa có nông trại.",
                }

            if not farm.is_train_event:
                return {
                    "success": False,
                    "message": "Hiện tại tàu hỏa chưa cập bến farm của bạn.",
                }

            member = memberRepository.findByUserId(userId)

            if member is None:
                return {
                    "success": False,
                    "message": "Không tìm thấy dữ liệu member của bạn.",
                }

            trainEvent = farmTrainEventRepository.findOpeningEventWithItem()

            if trainEvent is None:
                farmRepository.updateTrainEventFlag(farm, False)
                session.commit()

                return {
                    "success": False,
                    "message": "Hiện tại không có sự kiện tàu hỏa nào đang mở.",
                }

            completedHistory = farmTrainEventHistoryRepository.findByTrainEventIdAndFarmId(
                trainEventId=trainEvent.id,
                farmId=farm.id,
            )

            if completedHistory is not None:
                farmRepository.updateTrainEventFlag(farm, False)
                session.commit()

                return {
                    "success": False,
                    "message": "Farm của bạn đã giao hàng cho chuyến tàu này rồi.",
                }

            requiredItem = trainEvent.requiredItem

            if requiredItem is None:
                return {
                    "success": False,
                    "message": "Dữ liệu item tàu yêu cầu không hợp lệ.",
                }

            inventory = userInventoryRepository.findByUserIdAndItemId(
                userId=userId,
                itemId=requiredItem.id,
            )

            currentQuantity = inventory.quantity if inventory is not None else 0

            if currentQuantity < trainEvent.required_quantity:
                return {
                    "success": False,
                    "message": (
                        f"Tàu hỏa yêu cầu **{self.formatNumber(trainEvent.required_quantity)}** "
                        f"{self.buildItemText(requiredItem)}, "
                        f"bạn hiện có **{self.formatNumber(currentQuantity)}**."
                    ),
                }

            userInventoryRepository.decreaseQuantity(
                userInventory=inventory,
                quantity=trainEvent.required_quantity,
            )

            member.chill_coin += trainEvent.reward_chill_coin

            farmRepository.increaseFarmExp(
                farm=farm,
                exp=trainEvent.reward_exp,
            )

            farmTrainEventHistoryRepository.create(
                trainEventId=trainEvent.id,
                farmId=farm.id,
                userId=userId,
                deliveredItemId=requiredItem.id,
                deliveredQuantity=trainEvent.required_quantity,
                rewardChillCoin=trainEvent.reward_chill_coin,
                rewardExp=trainEvent.reward_exp,
            )

            farmRepository.updateTrainEventFlag(farm, False)

            session.commit()

            chillCoinEmoji = FARM_GAME_EMOJI["chill_coin"]
            expEmoji = FARM_GAME_EMOJI["exp"]

            return {
                "success": True,
                "message": (
                    f"Bạn đã chất **{self.formatNumber(trainEvent.required_quantity)}** "
                    f"{self.buildItemText(requiredItem)} lên tàu.\n"
                    f"Nhận được **{self.formatNumber(trainEvent.reward_chill_coin)}** {chillCoinEmoji}"
                    f"và {expEmoji} **{self.formatNumber(trainEvent.reward_exp)}**."
                ),
            }

    def buildItemText(self, item):
        itemEmoji = FARM_GAME_EMOJI.get(item.icon_image_key)

        if itemEmoji is None:
            return f"**{item.name}**"

        return f"{itemEmoji} **{item.name}**"

    def formatNumber(self, number: int):
        return f"{number:,}"