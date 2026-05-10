from bot.models.roleShop import RoleShop
from sqlalchemy import asc, desc


class RoleShopRepository:
    def __init__(self, session):
        self.session = session

    def findByRoleId(self, roleId: int):
        return (
            self.session.query(RoleShop)
            .filter(RoleShop.role_id == roleId)
            .first()
        )

    def createRoleShop(self, roleId: int, priceCowoncy: int, priceChillCoin: int):
        roleShop = RoleShop(
            role_id=roleId,
            price_cowoncy=priceCowoncy,
            price_chill_coin=priceChillCoin,
            valid_days=30,
            is_active=True,
        )

        self.session.add(roleShop)
        return roleShop

    def findActiveRoleShops(self):
        return (
            self.session.query(RoleShop)
            .filter(RoleShop.is_active.is_(True))
            .order_by(asc(RoleShop.sort_order), asc(RoleShop.id))
            .all()
        )

    def findActiveByRoleId(self, roleId: int):
        return (
            self.session.query(RoleShop)
            .filter(
                RoleShop.role_id == roleId,
                RoleShop.is_active.is_(True),
            )
            .first()
        )