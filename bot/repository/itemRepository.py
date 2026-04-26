from bot.models.items import Item


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