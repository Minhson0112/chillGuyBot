from bot.config.database import getDbSession
from bot.repository.roleShopRepository import RoleShopRepository


class RoleShopService:
    def createSellRole(self, roleId: int, priceCowoncy: int, priceChillCoin: int):
        if priceCowoncy < 0:
            return {
                "success": False,
                "message": "Giá cowoncy không được nhỏ hơn 0.",
            }

        if priceChillCoin < 0:
            return {
                "success": False,
                "message": "Giá chill coin không được nhỏ hơn 0.",
            }

        if priceCowoncy == 0 and priceChillCoin == 0:
            return {
                "success": False,
                "message": "Ít nhất một loại giá phải lớn hơn 0.",
            }

        with getDbSession() as session:
            roleShopRepository = RoleShopRepository(session)

            existingRoleShop = roleShopRepository.findByRoleId(roleId)

            if existingRoleShop is not None:
                return {
                    "success": False,
                    "message": "Role này đã được đăng bán rồi.",
                }

            roleShopRepository.createRoleShop(
                roleId=roleId,
                priceCowoncy=priceCowoncy,
                priceChillCoin=priceChillCoin,
            )

            session.commit()

            return {
                "success": True,
                "message": "Đã thêm role vào shop thành công.",
            }