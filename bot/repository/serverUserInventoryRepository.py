from bot.models.serverUserInventory import ServerUserInventory


class ServerUserInventoryRepository:
    def __init__(self, session):
        self.session = session

    def findByUserIdAndItemId(self, userId: int, itemId: int):
        return (
            self.session.query(ServerUserInventory)
            .filter(
                ServerUserInventory.user_id == userId,
                ServerUserInventory.item_id == itemId,
            )
            .first()
        )

    def findByUserId(self, userId: int):
        return (
            self.session.query(ServerUserInventory)
            .filter(ServerUserInventory.user_id == userId)
            .order_by(ServerUserInventory.item_id.asc())
            .all()
        )

    def upsertQuantity(self, userId: int, itemId: int, quantity: int):
        serverUserInventory = self.findByUserIdAndItemId(
            userId=userId,
            itemId=itemId,
        )

        if serverUserInventory is None:
            serverUserInventory = ServerUserInventory(
                user_id=userId,
                item_id=itemId,
                quantity=quantity,
            )
            self.session.add(serverUserInventory)
            self.session.flush()
            return serverUserInventory

        serverUserInventory.quantity += quantity
        self.session.flush()
        return serverUserInventory
