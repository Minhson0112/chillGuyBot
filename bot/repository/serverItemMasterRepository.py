from bot.models.serverItemMaster import ServerItemMaster


class ServerItemMasterRepository:
    def __init__(self, session):
        self.session = session

    def findAll(self):
        return (
            self.session.query(ServerItemMaster)
            .order_by(ServerItemMaster.type.asc(), ServerItemMaster.id.asc())
            .all()
        )

    def findActiveById(self, serverItemId: int):
        return (
            self.session.query(ServerItemMaster)
            .filter(
                ServerItemMaster.id == serverItemId,
                ServerItemMaster.is_active.is_(True),
            )
            .first()
        )
