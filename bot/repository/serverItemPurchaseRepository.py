from bot.enums.serverItemPurchaseStatus import ServerItemPurchaseStatus
from bot.models.serverItemMaster import ServerItemMaster
from bot.models.serverItemPurchase import ServerItemPurchase


class ServerItemPurchaseRepository:
    def __init__(self, session):
        self.session = session

    def createPendingPurchase(
        self,
        userId: int,
        itemId: int,
        quantity: int,
        registeredAt,
    ):
        serverItemPurchase = ServerItemPurchase(
            user_id=userId,
            item_id=itemId,
            quantity=quantity,
            status=ServerItemPurchaseStatus.PENDING_PAYMENT.value,
            registered_at=registeredAt,
        )

        self.session.add(serverItemPurchase)
        self.session.flush()
        return serverItemPurchase

    def findById(self, serverItemPurchaseId: int):
        return (
            self.session.query(ServerItemPurchase)
            .filter(ServerItemPurchase.id == serverItemPurchaseId)
            .first()
        )

    def findPendingPurchasesByUserId(self, userId: int):
        return (
            self.session.query(ServerItemPurchase)
            .join(ServerItemMaster, ServerItemMaster.id == ServerItemPurchase.item_id)
            .filter(
                ServerItemPurchase.user_id == userId,
                ServerItemPurchase.status == ServerItemPurchaseStatus.PENDING_PAYMENT.value,
            )
            .all()
        )
