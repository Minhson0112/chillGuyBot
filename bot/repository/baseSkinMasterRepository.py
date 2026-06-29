from bot.models.baseSkinMaster import BaseSkinMaster


class BaseSkinMasterRepository:
    def __init__(self, session):
        self.session = session

    def findById(self, baseSkinId: int):
        return (
            self.session.query(BaseSkinMaster)
            .filter(BaseSkinMaster.id == baseSkinId)
            .first()
        )

    def findByCode(self, code: str):
        return (
            self.session.query(BaseSkinMaster)
            .filter(BaseSkinMaster.code == code)
            .first()
        )

    def findActive(self):
        return (
            self.session.query(BaseSkinMaster)
            .filter(BaseSkinMaster.is_active.is_(True))
            .order_by(BaseSkinMaster.required_farm_level.asc(), BaseSkinMaster.id.asc())
            .all()
        )
