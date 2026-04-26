from sqlalchemy import asc
from sqlalchemy.orm import joinedload
from bot.models.items import Item
from bot.models.userInventory import UserInventory

from bot.models.userInventory import UserInventory


class UserInventoryRepository:
    def __init__(self, session):
        self.session = session

    def findById(self, userInventoryId: int):
        return (
            self.session.query(UserInventory)
            .filter(UserInventory.id == userInventoryId)
            .first()
        )

    def findByUserIdAndItemId(self, userId: int, itemId: int):
        return (
            self.session.query(UserInventory)
            .filter(UserInventory.user_id == userId)
            .filter(UserInventory.item_id == itemId)
            .first()
        )

    def findByUserId(self, userId: int):
        return (
            self.session.query(UserInventory)
            .options(joinedload(UserInventory.item))
            .filter(UserInventory.user_id == userId)
            .order_by(asc(UserInventory.id))
            .all()
        )

    def findSiloItemsByUserIdAndPage(self, userId: int, page: int, perPage: int):
        offset = (page - 1) * perPage

        return (
            self.session.query(UserInventory)
            .join(UserInventory.item)
            .options(joinedload(UserInventory.item))
            .filter(UserInventory.user_id == userId)
            .filter(UserInventory.quantity > 0)
            .filter(Item.type_code.in_(["crop", "seed"]))
            .order_by(asc(UserInventory.id))
            .offset(offset)
            .limit(perPage)
            .all()
        )

    def countSiloItemsByUserId(self, userId: int):
        return (
            self.session.query(UserInventory)
            .join(UserInventory.item)
            .filter(UserInventory.user_id == userId)
            .filter(UserInventory.quantity > 0)
            .filter(Item.type_code.in_(["crop", "seed"]))
            .count()
        )

    def findBarnItemsByUserIdAndPage(self, userId: int, page: int, perPage: int):
        offset = (page - 1) * perPage

        return (
            self.session.query(UserInventory)
            .join(UserInventory.item)
            .options(joinedload(UserInventory.item))
            .filter(UserInventory.user_id == userId)
            .filter(UserInventory.quantity > 0)
            .filter(~Item.type_code.in_(["crop", "seed"]))
            .order_by(asc(UserInventory.id))
            .offset(offset)
            .limit(perPage)
            .all()
        )

    def countBarnItemsByUserId(self, userId: int):
        return (
            self.session.query(UserInventory)
            .join(UserInventory.item)
            .filter(UserInventory.user_id == userId)
            .filter(UserInventory.quantity > 0)
            .filter(~Item.type_code.in_(["crop", "seed"]))
            .count()
        )

    def create(self, userId: int, itemId: int, quantity: int):
        userInventory = UserInventory(
            user_id=userId,
            item_id=itemId,
            quantity=quantity,
        )

        self.session.add(userInventory)
        self.session.flush()

        return userInventory

    def increaseQuantity(self, userInventory: UserInventory, quantity: int):
        userInventory.quantity += quantity
        self.session.flush()

        return userInventory

    def decreaseQuantity(self, userInventory: UserInventory, quantity: int):
        userInventory.quantity -= quantity

        if userInventory.quantity < 0:
            userInventory.quantity = 0

        self.session.flush()

        return userInventory

    def updateQuantity(self, userInventory: UserInventory, quantity: int):
        userInventory.quantity = quantity
        self.session.flush()

        return userInventory

    def addOrCreate(self, userId: int, itemId: int, quantity: int):
        userInventory = self.findByUserIdAndItemId(userId, itemId)

        if userInventory is None:
            return self.create(userId, itemId, quantity)

        return self.increaseQuantity(userInventory, quantity)

    def delete(self, userInventory: UserInventory):
        self.session.delete(userInventory)
        self.session.flush()