from bot.models.items import Item
from sqlalchemy import asc
from bot.models.foodRecipe import FoodRecipe
import random


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
    
    def findActiveByNameKeyword(self, itemName: str):
        keyword = itemName.strip()

        exactItem = (
            self.session.query(Item)
            .filter(Item.is_active == 1)
            .filter(Item.name == keyword)
            .order_by(asc(Item.id))
            .first()
        )

        if exactItem is not None:
            return exactItem

        return (
            self.session.query(Item)
            .filter(Item.is_active == 1)
            .filter(Item.name.like(f"%{keyword}%"))
            .order_by(asc(Item.id))
            .first()
        )
    
    def findRandomFoodItemWithRecipe(self):
        rows = (
            self.session.query(Item, FoodRecipe)
            .join(FoodRecipe, FoodRecipe.result_item_id == Item.id)
            .filter(Item.type_code == "food")
            .filter(Item.is_active.is_(True))
            .all()
        )

        if not rows:
            return None

        return random.choice(rows)