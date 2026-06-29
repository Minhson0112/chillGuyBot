from sqlalchemy.orm import joinedload

from bot.models.memberBaseSkinInventory import MemberBaseSkinInventory


class MemberBaseSkinInventoryRepository:
    def __init__(self, session):
        self.session = session

    def findByUserIdAndBaseSkinId(self, userId: int, baseSkinId: int):
        return (
            self.session.query(MemberBaseSkinInventory)
            .filter(MemberBaseSkinInventory.user_id == userId)
            .filter(MemberBaseSkinInventory.base_skin_id == baseSkinId)
            .first()
        )

    def findByUserId(self, userId: int):
        return (
            self.session.query(MemberBaseSkinInventory)
            .options(joinedload(MemberBaseSkinInventory.baseSkin))
            .filter(MemberBaseSkinInventory.user_id == userId)
            .order_by(MemberBaseSkinInventory.id.asc())
            .all()
        )

    def findUsingByUserId(self, userId: int):
        return (
            self.session.query(MemberBaseSkinInventory)
            .options(joinedload(MemberBaseSkinInventory.baseSkin))
            .filter(MemberBaseSkinInventory.user_id == userId)
            .filter(MemberBaseSkinInventory.is_using.is_(True))
            .order_by(MemberBaseSkinInventory.id.asc())
            .first()
        )

    def findByUserIdForUpdate(self, userId: int):
        return (
            self.session.query(MemberBaseSkinInventory)
            .filter(MemberBaseSkinInventory.user_id == userId)
            .order_by(MemberBaseSkinInventory.id.asc())
            .with_for_update()
            .all()
        )

    def setUsing(self, inventories, selectedInventoryId: int):
        selectedInventory = None

        for inventory in inventories:
            inventory.is_using = inventory.id == selectedInventoryId

            if inventory.is_using:
                selectedInventory = inventory

        self.session.flush()

        return selectedInventory

    def create(self, userId: int, baseSkinId: int, isUsing: bool = False):
        inventory = MemberBaseSkinInventory(
            user_id=userId,
            base_skin_id=baseSkinId,
            is_using=isUsing,
        )

        self.session.add(inventory)
        self.session.flush()

        return inventory
