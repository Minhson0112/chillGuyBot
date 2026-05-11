from bot.models.memberRolePurchase import MemberRolePurchase
from bot.enums.rolePurchaseStatus import RolePurchaseStatus
from bot.models.roleShop import RoleShop


class MemberRolePurchaseRepository:
    def __init__(self, session):
        self.session = session

    def findByUserIdAndRoleShopId(self, userId: int, roleShopId: int):
        return (
            self.session.query(MemberRolePurchase)
            .filter(
                MemberRolePurchase.user_id == userId,
                MemberRolePurchase.role_shop_id == roleShopId,
            )
            .first()
        )

    def createPendingPurchase(self, userId: int, roleShopId: int, registeredAt):
        memberRolePurchase = MemberRolePurchase(
            user_id=userId,
            role_shop_id=roleShopId,
            status=RolePurchaseStatus.PENDING_PAYMENT.value,
            registered_at=registeredAt,
        )

        self.session.add(memberRolePurchase)
        return memberRolePurchase

    def findPendingPurchasesByUserId(self, userId: int):
        return (
            self.session.query(MemberRolePurchase)
            .join(RoleShop, RoleShop.id == MemberRolePurchase.role_shop_id)
            .filter(
                MemberRolePurchase.user_id == userId,
                MemberRolePurchase.status == RolePurchaseStatus.PENDING_PAYMENT.value,
            )
            .all()
        )

    def findPendingPurchaseByUserId(self, userId: int):
        return (
            self.session.query(MemberRolePurchase)
            .join(RoleShop, RoleShop.id == MemberRolePurchase.role_shop_id)
            .filter(
                MemberRolePurchase.user_id == userId,
                MemberRolePurchase.status == RolePurchaseStatus.PENDING_PAYMENT.value,
            )
            .first()
        )

    def findById(self, memberRolePurchaseId: int):
        return (
            self.session.query(MemberRolePurchase)
            .filter(MemberRolePurchase.id == memberRolePurchaseId)
            .first()
        )