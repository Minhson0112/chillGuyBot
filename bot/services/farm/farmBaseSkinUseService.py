from bot.config.database import getDbSession
from bot.repository.memberBaseSkinInventoryRepository import MemberBaseSkinInventoryRepository


class FarmBaseSkinUseService:
    def useBaseSkin(self, userId: int, inventoryId: int):
        with getDbSession() as session:
            memberBaseSkinInventoryRepository = MemberBaseSkinInventoryRepository(session)

            inventories = memberBaseSkinInventoryRepository.findByUserIdForUpdate(userId)
            selectedInventory = next(
                (
                    inventory
                    for inventory in inventories
                    if inventory.id == inventoryId
                ),
                None,
            )

            if selectedInventory is None:
                return {
                    "success": False,
                    "message": (
                        f"Không tìm thấy base skin với ID kho **{inventoryId}** "
                        "trong kho của bạn."
                    ),
                }

            if selectedInventory.baseSkin is None:
                return {
                    "success": False,
                    "message": "Dữ liệu base skin không hợp lệ.",
                }

            if selectedInventory.is_using:
                return {
                    "success": False,
                    "message": f"Bạn đang sử dụng base skin **{selectedInventory.baseSkin.name}** rồi.",
                }

            memberBaseSkinInventoryRepository.setUsing(
                inventories=inventories,
                selectedInventoryId=selectedInventory.id,
            )

            session.commit()

            return {
                "success": True,
                "message": f"Đã chuyển sang sử dụng base skin **{selectedInventory.baseSkin.name}**.",
            }
