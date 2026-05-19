from sqlalchemy import asc
from sqlalchemy.orm import joinedload

from bot.models.shopItem import ShopItem


class ShopItemRepository:
    def __init__(self, session):
        self.session = session

    def findById(self, shopItemId: int):
        return (
            self.session.query(ShopItem)
            .filter(ShopItem.id == shopItemId)
            .first()
        )

    def findByIdWithItem(self, shopItemId: int):
        return (
            self.session.query(ShopItem)
            .options(joinedload(ShopItem.item))
            .filter(ShopItem.id == shopItemId)
            .first()
        )

    def findByItemId(self, itemId: int):
        return (
            self.session.query(ShopItem)
            .filter(ShopItem.item_id == itemId)
            .first()
        )

    def findVisibleItems(self):
        return (
            self.session.query(ShopItem)
            .options(joinedload(ShopItem.item))
            .filter(ShopItem.is_visible.is_(True))
            .order_by(asc(ShopItem.sort_order), asc(ShopItem.id))
            .all()
        )

    def findActiveVisibleItems(self):
        return (
            self.session.query(ShopItem)
            .options(joinedload(ShopItem.item))
            .filter(ShopItem.is_visible.is_(True))
            .filter(ShopItem.is_active.is_(True))
            .order_by(asc(ShopItem.sort_order), asc(ShopItem.id))
            .all()
        )

    def findAvailableItemsByFarmLevel(self, farmLevel: int):
        return (
            self.session.query(ShopItem)
            .options(joinedload(ShopItem.item))
            .filter(ShopItem.is_visible.is_(True))
            .filter(ShopItem.is_active.is_(True))
            .filter(ShopItem.required_farm_level <= farmLevel)
            .order_by(asc(ShopItem.sort_order), asc(ShopItem.id))
            .all()
        )

    def findVisibleItemsByPage(self, page: int, perPage: int):
        offset = (page - 1) * perPage

        return (
            self.session.query(ShopItem)
            .options(joinedload(ShopItem.item))
            .filter(ShopItem.is_visible.is_(True))
            .order_by(asc(ShopItem.sort_order), asc(ShopItem.id))
            .offset(offset)
            .limit(perPage)
            .all()
        )

    def countVisibleItems(self):
        return (
            self.session.query(ShopItem)
            .filter(ShopItem.is_visible.is_(True))
            .count()
        )

    def create(
        self,
        itemId: int,
        buyPrice: int,
        requiredFarmLevel: int = 1,
        isVisible: bool = True,
        isActive: bool = True,
        sortOrder: int = 0,
    ):
        shopItem = ShopItem(
            item_id=itemId,
            buy_price=buyPrice,
            required_farm_level=requiredFarmLevel,
            is_visible=isVisible,
            is_active=isActive,
            sort_order=sortOrder,
        )

        self.session.add(shopItem)
        self.session.flush()

        return shopItem

    def updatePrice(self, shopItem: ShopItem, buyPrice: int):
        shopItem.buy_price = buyPrice
        self.session.flush()

        return shopItem

    def updateRequiredFarmLevel(self, shopItem: ShopItem, requiredFarmLevel: int):
        shopItem.required_farm_level = requiredFarmLevel
        self.session.flush()

        return shopItem

    def updateSortOrder(self, shopItem: ShopItem, sortOrder: int):
        shopItem.sort_order = sortOrder
        self.session.flush()

        return shopItem

    def show(self, shopItem: ShopItem):
        shopItem.is_visible = True
        self.session.flush()

        return shopItem

    def hide(self, shopItem: ShopItem):
        shopItem.is_visible = False
        self.session.flush()

        return shopItem

    def activate(self, shopItem: ShopItem):
        shopItem.is_active = True
        self.session.flush()

        return shopItem

    def deactivate(self, shopItem: ShopItem):
        shopItem.is_active = False
        self.session.flush()

        return shopItem