from bot.models.farmTrainEventHistory import FarmTrainEventHistory


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