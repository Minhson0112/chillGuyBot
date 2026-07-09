from bot.models.farmTrainEventHistory import FarmTrainEventHistory
from datetime import datetime

from sqlalchemy import asc, desc, func


class FarmTrainEventHistoryRepository:
    def __init__(self, session):
        self.session = session

    def create(
        self,
        trainEventId: int,
        farmId: int,
        userId: int,
        deliveredItemId: int,
        deliveredQuantity: int,
        rewardChillCoin: int,
        rewardExp: int,
    ):
        farmTrainEventHistory = FarmTrainEventHistory(
            train_event_id=trainEventId,
            farm_id=farmId,
            user_id=userId,
            delivered_item_id=deliveredItemId,
            delivered_quantity=deliveredQuantity,
            reward_chill_coin=rewardChillCoin,
            reward_exp=rewardExp,
        )

        self.session.add(farmTrainEventHistory)
        self.session.flush()

        return farmTrainEventHistory

    def findByTrainEventIdAndFarmId(
        self,
        trainEventId: int,
        farmId: int,
    ):
        return (
            self.session.query(FarmTrainEventHistory)
            .filter(FarmTrainEventHistory.train_event_id == trainEventId)
            .filter(FarmTrainEventHistory.farm_id == farmId)
            .first()
        )
    
    def findTop10CompletedByMonth(
        self,
        year: int,
        month: int,
    ):
        startAt = datetime(year, month, 1)

        if month == 12:
            endAt = datetime(year + 1, 1, 1)
        else:
            endAt = datetime(year, month + 1, 1)

        completedCount = func.count(FarmTrainEventHistory.id).label("completed_count")

        return (
            self.session.query(
                FarmTrainEventHistory.user_id,
                completedCount,
            )
            .filter(FarmTrainEventHistory.created_at >= startAt)
            .filter(FarmTrainEventHistory.created_at < endAt)
            .group_by(FarmTrainEventHistory.user_id)
            .order_by(
                desc(completedCount),
                asc(FarmTrainEventHistory.user_id),
            )
            .limit(10)
            .all()
        )

    def countByUserId(
        self,
        userId: int,
    ):
        return (
            self.session.query(func.count(FarmTrainEventHistory.id))
            .filter(FarmTrainEventHistory.user_id == userId)
            .scalar()
            or 0
        )
