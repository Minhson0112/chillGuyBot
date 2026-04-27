from datetime import datetime

from sqlalchemy import asc, desc
from sqlalchemy.orm import joinedload

from bot.models.fishingHistory import FishingHistory


class FishingHistoryRepository:
    def __init__(self, session):
        self.session = session

    def create(
        self,
        userId: int,
        itemId: int,
        weightKg,
    ):
        fishingHistory = FishingHistory(
            user_id=userId,
            item_id=itemId,
            weight_kg=weightKg,
        )

        self.session.add(fishingHistory)
        self.session.flush()

        return fishingHistory

    def findTop10(self):
        return (
            self.session.query(FishingHistory)
            .options(
                joinedload(FishingHistory.member),
                joinedload(FishingHistory.item),
            )
            .order_by(
                desc(FishingHistory.weight_kg),
                asc(FishingHistory.caught_at),
                asc(FishingHistory.id),
            )
            .limit(10)
            .all()
        )

    def findTop10ByMonth(
        self,
        year: int,
        month: int,
    ):
        startAt = datetime(year, month, 1)

        if month == 12:
            endAt = datetime(year + 1, 1, 1)
        else:
            endAt = datetime(year, month + 1, 1)

        return (
            self.session.query(FishingHistory)
            .options(
                joinedload(FishingHistory.member),
                joinedload(FishingHistory.item),
            )
            .filter(FishingHistory.caught_at >= startAt)
            .filter(FishingHistory.caught_at < endAt)
            .order_by(
                desc(FishingHistory.weight_kg),
                asc(FishingHistory.caught_at),
                asc(FishingHistory.id),
            )
            .limit(10)
            .all()
        )

    def findByUserId(self, userId: int):
        return (
            self.session.query(FishingHistory)
            .options(
                joinedload(FishingHistory.item),
            )
            .filter(FishingHistory.user_id == userId)
            .order_by(
                desc(FishingHistory.weight_kg),
                desc(FishingHistory.caught_at),
                desc(FishingHistory.id),
            )
            .all()
        )

    def findBestByUserId(self, userId: int):
        return (
            self.session.query(FishingHistory)
            .options(
                joinedload(FishingHistory.item),
            )
            .filter(FishingHistory.user_id == userId)
            .order_by(
                desc(FishingHistory.weight_kg),
                asc(FishingHistory.caught_at),
                asc(FishingHistory.id),
            )
            .first()
        )

    def findRecentByUserId(
        self,
        userId: int,
        limit: int = 10,
    ):
        return (
            self.session.query(FishingHistory)
            .options(
                joinedload(FishingHistory.item),
            )
            .filter(FishingHistory.user_id == userId)
            .order_by(
                desc(FishingHistory.caught_at),
                desc(FishingHistory.id),
            )
            .limit(limit)
            .all()
        )