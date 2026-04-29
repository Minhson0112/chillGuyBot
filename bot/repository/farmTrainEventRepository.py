from datetime import datetime

from sqlalchemy import asc, desc
from sqlalchemy.orm import joinedload

from bot.models.farmTrainEvent import FarmTrainEvent

class FarmTrainEventRepository:
    def __init__(self, session):
        self.session = session

    def create(
        self,
        requiredItemId: int,
        requiredQuantity: int,
        rewardChillCoin: int,
        rewardExp: int,
        createdByUserId: int,
    ):
        farmTrainEvent = FarmTrainEvent(
            required_item_id=requiredItemId,
            required_quantity=requiredQuantity,
            reward_chill_coin=rewardChillCoin,
            reward_exp=rewardExp,
            is_completed=False,
            created_by_user_id=createdByUserId,
        )

        self.session.add(farmTrainEvent)
        self.session.flush()

        return farmTrainEvent
    
    def findById(self, trainEventId: int):
        return (
            self.session.query(FarmTrainEvent)
            .filter(FarmTrainEvent.id == trainEventId)
            .first()
        )

    def findOpeningEvent(self):
        return (
            self.session.query(FarmTrainEvent)
            .filter(FarmTrainEvent.closed_at.is_(None))
            .filter(FarmTrainEvent.is_completed.is_(False))
            .order_by(desc(FarmTrainEvent.created_at), desc(FarmTrainEvent.id))
            .first()
        )

    def closeEvent(self, farmTrainEvent: FarmTrainEvent):
        farmTrainEvent.closed_at = datetime.now()

        self.session.flush()

        return farmTrainEvent
    
    def findOpeningEventWithItem(self):
        return (
            self.session.query(FarmTrainEvent)
            .options(joinedload(FarmTrainEvent.requiredItem))
            .filter(FarmTrainEvent.closed_at.is_(None))
            .filter(FarmTrainEvent.is_completed.is_(False))
            .order_by(
                desc(FarmTrainEvent.created_at),
                desc(FarmTrainEvent.id),
            )
            .first()
        )
