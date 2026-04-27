from bot.models.items import Item
from sqlalchemy import asc


class ItemRepository:
    def __init__(self, session):
        self.session = session

    def findById(self, itemId: int):
        return (
            self.session.query(Item)
            .filter(Item.id == itemId)
            .first()
        )

    def findByCode(self, code: str):
        return (
            self.session.query(Item)
            .filter(Item.code == code)
            .first()
        )
    
    def findActiveItemsByTypeCode(self, typeCode: str):
        return (
            self.session.query(Item)
            .filter(Item.type_code == typeCode)
            .filter(Item.is_active.is_(True))
            .order_by(asc(Item.id))
            .all()
        )