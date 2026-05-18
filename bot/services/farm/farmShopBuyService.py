from bot.config.database import getDbSession
from bot.config.emoji import FARM_GAME_EMOJI
from bot.repository.farmRepository import FarmRepository
from bot.repository.memberRepository import MemberRepository
from bot.repository.shopItemRepository import ShopItemRepository
from bot.repository.userInventoryRepository import UserInventoryRepository
from bot.services.farm.farmAnimalBuyService import FarmAnimalBuyService
from bot.services.farm.farmToolBuyService import FarmToolBuyService


class FarmShopBuyService:
    def __init__(self):
        self.farmAnimalBuyService = FarmAnimalBuyService()
        self.farmToolBuyService = FarmToolBuyService()

    def buyShopItem(
        self,
        userId: int,
        shopItemId: int,
        quantity: int = 1,
    ):
        if quantity is None:
            quantity = 1

        if quantity <= 0:
            return {
                "success": False,
                "message": "Số lượng mua phải lớn hơn 0.",
            }

        with getDbSession() as session:
            memberRepository = MemberRepository(session)
            farmRepository = FarmRepository(session)
            shopItemRepository = ShopItemRepository(session)
            userInventoryRepository = UserInventoryRepository(session)

            member = memberRepository.findByUserId(userId)

            if member is None:
                return {
                    "success": False,
                    "message": "Không tìm thấy dữ liệu member của bạn.",
                }

            farm = farmRepository.findByUserId(userId)

            if farm is None:
                return {
                    "success": False,
                    "message": "Bạn chưa có nông trại.",
                }

            shopItem = shopItemRepository.findByIdWithItem(shopItemId)

            if shopItem is None or shopItem.item is None:
                return {
                    "success": False,
                    "message": f"Không tìm thấy item trong shop với ID **{shopItemId}**.",
                }

            if not shopItem.is_visible or not shopItem.is_active:
                return {
                    "success": False,
                    "message": "Item này hiện không thể mua.",
                }

            item = shopItem.item
            itemText = self.buildItemText(item)
            chillCoinEmoji = FARM_GAME_EMOJI["chill_coin"]

            if farm.farm_level < shopItem.required_farm_level:
                return {
                    "success": False,
                    "message": (
                        f"{itemText} yêu cầu farm level **{shopItem.required_farm_level}**, "
                        f"farm của bạn hiện level **{farm.farm_level}**."
                    ),
                }

            if self.farmAnimalBuyService.canHandle(item.code) and quantity != 1:
                return {
                    "success": False,
                    "message": f"{itemText} chỉ có thể mua từng con một.",
                }

            if self.farmToolBuyService.canHandle(item) and quantity != 1:
                return {
                    "success": False,
                    "message": f"{itemText} chỉ có thể mua từng dụng cụ một.",
                }

            totalPrice = shopItem.buy_price * quantity

            if member.chill_coin < totalPrice:
                return {
                    "success": False,
                    "message": (
                        f"Mua **{quantity}** {itemText} cần "
                        f"**{self.formatNumber(totalPrice)}** {chillCoinEmoji}, "
                        f"bạn chỉ có **{self.formatNumber(member.chill_coin)}** {chillCoinEmoji}."
                    ),
                }

            if self.farmAnimalBuyService.canHandle(item.code):
                animalBuyResult = self.farmAnimalBuyService.buyAnimal(
                    session=session,
                    farm=farm,
                    itemCode=item.code,
                )

                if not animalBuyResult["success"]:
                    return animalBuyResult

                member.chill_coin -= totalPrice
                session.commit()

                return {
                    "success": True,
                    "message": (
                        f"{animalBuyResult['message']} "
                        f"Bạn đã trả **{self.formatNumber(totalPrice)}** {chillCoinEmoji}."
                    ),
                }

            if self.farmToolBuyService.canHandle(item):
                toolBuyResult = self.farmToolBuyService.buyTool(
                    session=session,
                    userId=userId,
                    item=item,
                )

                if not toolBuyResult["success"]:
                    return toolBuyResult

                member.chill_coin -= totalPrice
                session.commit()

                userTool = toolBuyResult["userTool"]
                toolTemplate = toolBuyResult["toolTemplate"]

                return {
                    "success": True,
                    "message": (
                        f"Bạn đã mua {itemText} với "
                        f"**{self.formatNumber(totalPrice)}** {chillCoinEmoji}. "
                        f"Độ bền: **{toolTemplate.max_durability}**. "
                        f"ID tool: **{userTool.id}**"
                    ),
                }

            member.chill_coin -= totalPrice

            userInventory = userInventoryRepository.addOrCreate(
                userId=userId,
                itemId=shopItem.item_id,
                quantity=quantity,
            )

            session.commit()

            return {
                "success": True,
                "message": (
                    f"Bạn đã mua **{quantity}** {itemText} với "
                    f"**{self.formatNumber(totalPrice)}** {chillCoinEmoji}. "
                    f"ID kho: **{userInventory.id}**"
                ),
            }

    def buildItemText(self, item):
        itemEmoji = FARM_GAME_EMOJI.get(item.icon_image_key)

        if itemEmoji is None:
            return f"**{item.name}**"

        return f"{itemEmoji} **{item.name}**"

    def formatNumber(self, number: int):
        return f"{number:,}"