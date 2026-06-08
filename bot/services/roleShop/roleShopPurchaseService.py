from datetime import datetime

from bot.config.database import getDbSession
from bot.enums.memberPaymentTargetType import MemberPaymentTargetType
from bot.enums.rolePurchaseStatus import RolePurchaseStatus
from bot.repository.memberPaymentTransactionRepository import MemberPaymentTransactionRepository
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
            memberPaymentTransactionRepository = MemberPaymentTransactionRepository(session)
            memberRolePurchaseRepository = MemberRolePurchaseRepository(session)

            roleShop = roleShopRepository.findActiveByRoleId(roleId)

            if roleShop is None:
                return {
                    "success": False,
                    "message": "Role này hiện không được bán trong shop.",
                }

            requiredCowoncyAmount = self.normalizePrice(roleShop.price_cowoncy)
            requiredChillCoinAmount = self.normalizePrice(roleShop.price_chill_coin)

            if requiredCowoncyAmount is None and requiredChillCoinAmount is None:
                return {
                    "success": False,
                    "message": "Role này chưa có giá thanh toán hợp lệ.",
                }

            pendingPayment = memberPaymentTransactionRepository.findPendingPaymentByUserId(userId)

            if pendingPayment is not None:
                pendingRolePurchase = self.findPendingRolePurchase(
                    memberRolePurchaseRepository=memberRolePurchaseRepository,
                    pendingPayment=pendingPayment,
                )
                pendingRoleId = self.getPendingRoleId(pendingRolePurchase)

                if pendingRolePurchase is not None and pendingRolePurchase.role_shop_id == roleShop.id:
                    return {
                        "success": False,
                        "message": "Bạn đã đăng kí mua role này rồi. Vui lòng thanh toán hoặc dùng `cg cancelbuyrole` để hủy giao dịch.",
                        "pendingRoleId": pendingRoleId,
                    }

                if pendingRolePurchase is not None:
                    return {
                        "success": False,
                        "message": "Bạn đang có giao dịch mua role khác đang chờ thanh toán. Hãy thanh toán role đó trước rồi hãy mua thêm role mới.",
                        "pendingRoleId": pendingRoleId,
                    }

                return {
                    "success": False,
                    "message": "Bạn đang có giao dịch khác đang chờ thanh toán. Hãy thanh toán hoặc hủy giao dịch đó trước.",
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
                memberRolePurchase = memberRolePurchaseRepository.createPendingPurchase(
                    userId=userId,
                    roleShopId=roleShop.id,
                    registeredAt=now,
                )

            memberPaymentTransactionRepository.createPendingPayment(
                userId=userId,
                paymentTargetType=MemberPaymentTargetType.ROLE_SHOP.value,
                paymentTargetId=memberRolePurchase.id,
                requiredCowoncyAmount=requiredCowoncyAmount,
                requiredChillCoinAmount=requiredChillCoinAmount,
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

    def findPendingRolePurchase(
        self,
        memberRolePurchaseRepository: MemberRolePurchaseRepository,
        pendingPayment,
    ):
        if pendingPayment.payment_target_type != MemberPaymentTargetType.ROLE_SHOP.value:
            return None

        return memberRolePurchaseRepository.findById(pendingPayment.payment_target_id)

    def getPendingRoleId(self, pendingRolePurchase):
        if pendingRolePurchase is None:
            return None

        if pendingRolePurchase.role_shop is None:
            return None

        return pendingRolePurchase.role_shop.role_id

    def normalizePrice(self, price):
        if price is None or price <= 0:
            return None

        return price
