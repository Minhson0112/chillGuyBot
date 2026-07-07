from sqlalchemy import or_

from bot.models.couple import Couple


class CoupleRepository:
    def __init__(self, session):
        self.session = session

    def findActiveByUserId(self, userId: int):
        return (
            self.session.query(Couple)
            .filter(
                Couple.divorcing_at.is_(None),
                or_(
                    Couple.user_1_id == userId,
                    Couple.user_2_id == userId,
                ),
            )
            .first()
        )

    def findActiveByPair(self, user1Id: int, user2Id: int):
        firstUserId, secondUserId = self.normalizeUserPair(user1Id, user2Id)

        return (
            self.session.query(Couple)
            .filter(
                Couple.user_1_id == firstUserId,
                Couple.user_2_id == secondUserId,
                Couple.divorcing_at.is_(None),
            )
            .first()
        )

    def createCouple(
        self,
        user1Id: int,
        user2Id: int,
        intimacyPoints: int,
    ):
        firstUserId, secondUserId = self.normalizeUserPair(user1Id, user2Id)
        couple = Couple(
            user_1_id=firstUserId,
            user_2_id=secondUserId,
            intimacy_points=intimacyPoints,
        )

        self.session.add(couple)
        self.session.flush()
        return couple

    def normalizeUserPair(self, user1Id: int, user2Id: int):
        if user1Id < user2Id:
            return user1Id, user2Id

        return user2Id, user1Id
