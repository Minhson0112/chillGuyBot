from sqlalchemy import func, desc

from bot.models.owoDonateHistory import OwoDonateHistory


class OwoDonateHistoryRepository:
    def __init__(self, session):
        self.session = session

    def create(self, data):
        owoDonateHistory = OwoDonateHistory(**data)
        self.session.add(owoDonateHistory)
        self.session.flush()
        return owoDonateHistory

    def getTotalDonateBySenderUserId(self, senderUserId):
        totalDonate = (
            self.session.query(
                func.coalesce(func.sum(OwoDonateHistory.cowoncy_amount), 0)
            )
            .filter(OwoDonateHistory.sender_user_id == senderUserId)
            .scalar()
        )

        return totalDonate

    def getTopDonators(self, limit=10):
        return (
            self.session.query(
                OwoDonateHistory.sender_user_id,
                func.sum(OwoDonateHistory.cowoncy_amount).label("totalDonate"),
            )
            .group_by(OwoDonateHistory.sender_user_id)
            .order_by(desc("totalDonate"))
            .limit(limit)
            .all()
        )

    def getDonateHistoryBySenderUserId(self, senderUserId, limit=50):
        return (
            self.session.query(OwoDonateHistory)
            .filter(OwoDonateHistory.sender_user_id == senderUserId)
            .order_by(OwoDonateHistory.created_at.desc(), OwoDonateHistory.id.desc())
            .limit(limit)
            .all()
        )

    def countDonateBySenderUserId(self, senderUserId):
        return (
            self.session.query(func.count(OwoDonateHistory.id))
            .filter(OwoDonateHistory.sender_user_id == senderUserId)
            .scalar()
        )

    def getLatestDonateBySenderUserId(self, senderUserId):
        return (
            self.session.query(OwoDonateHistory)
            .filter(OwoDonateHistory.sender_user_id == senderUserId)
            .order_by(OwoDonateHistory.created_at.desc(), OwoDonateHistory.id.desc())
            .first()
        )
    
    def getTopDonators(self, limit=10):
        return (
            self.session.query(
                OwoDonateHistory.sender_user_id,
                func.sum(OwoDonateHistory.cowoncy_amount).label("totalDonate"),
            )
            .group_by(OwoDonateHistory.sender_user_id)
            .order_by(desc("totalDonate"))
            .limit(limit)
            .all()
        )
    
    def getDonateRankBySenderUserId(self, senderUserId):
        rows = (
            self.session.query(
                OwoDonateHistory.sender_user_id,
                func.sum(OwoDonateHistory.cowoncy_amount).label("totalDonate"),
            )
            .group_by(OwoDonateHistory.sender_user_id)
            .order_by(desc("totalDonate"))
            .all()
        )

        for index, row in enumerate(rows, start=1):
            if row.sender_user_id == senderUserId:
                return index

        return None