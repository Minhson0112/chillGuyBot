from datetime import datetime

from bot.config.database import getDbSession
from bot.enums.rolePurchaseStatus import RolePurchaseStatus
from bot.repository.memberRolePurchaseRepository import MemberRolePurchaseRepository
from bot.repository.roleShopRepository import RoleShopRepository


class RoleShopPurchaseService:
    def findActiveRoleShops(self):
        with getDbSession() as session:
            roleShopRepository = RoleShopRepository(session)
            roleShops = roleShopRepository.findActiveRoleShops()

            return [
                {
                    "id": roleShop.id,
                    "roleId": roleShop.role_id,
                    "priceCowoncy": roleShop.price_cowoncy,
                    "priceChillCoin": roleShop.price_chill_coin,
                    "validDays": roleShop.valid_days,
                }
                for roleShop in roleShops
            ]

    def createPendingPurchase(self, userId: int, roleId: int):
        now = datetime.now()

        with getDbSession() as session:
            roleShopRepository = RoleShopRepository(session)
            memberRolePurchaseRepository = MemberRolePurchaseRepository(session)

            roleShop = roleShopRepository.findActiveByRoleId(roleId)

            if roleShop is None:
                return {
                    "success": False,
                    "message": "Role này hiện không được bán trong shop.",
                }

            pendingPurchase = memberRolePurchaseRepository.findPendingPurchaseByUserId(userId)

            if pendingPurchase is not None:
                pendingRoleId = None

                if pendingPurchase.role_shop is not None:
                    pendingRoleId = pendingPurchase.role_shop.role_id

                if pendingPurchase.role_shop_id == roleShop.id:
                    return {
                        "success": False,
                        "message": "Bạn đã đăng kí mua role này rồi. Vui lòng thanh toán hoặc dùng `cg cancelbuyrole` để hủy giao dịch.",
                        "pendingRoleId": pendingRoleId,
                    }

                return {
                    "success": False,
                    "message": "Bạn đang có giao dịch mua role khác đang chờ thanh toán. Hãy thanh toán role đó trước rồi hãy mua thêm role mới.",
                    "pendingRoleId": pendingRoleId,
                }

            memberRolePurchase = memberRolePurchaseRepository.findByUserIdAndRoleShopId(
                userId=userId,
                roleShopId=roleShop.id,
            )

            if memberRolePurchase is not None:
                if memberRolePurchase.status == RolePurchaseStatus.PAID.value:
                    if memberRolePurchase.expired_at is None or memberRolePurchase.expired_at > now:
                        return {
                            "success": False,
                            "message": "Bạn đang sở hữu role này rồi.",
                        }

                memberRolePurchase.status = RolePurchaseStatus.PENDING_PAYMENT.value
                memberRolePurchase.registered_at = now
                memberRolePurchase.paid_at = None
                memberRolePurchase.expired_at = None
                memberRolePurchase.payment_type = None
                memberRolePurchase.payment_amount = None
            else:
                memberRolePurchaseRepository.createPendingPurchase(
                    userId=userId,
                    roleShopId=roleShop.id,
                    registeredAt=now,
                )

            session.commit()

            return {
                "success": True,
                "roleId": roleShop.role_id,
                "priceCowoncy": roleShop.price_cowoncy,
                "priceChillCoin": roleShop.price_chill_coin,
                "validDays": roleShop.valid_days,
            }