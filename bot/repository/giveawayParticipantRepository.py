from bot.enums.giveawayParticipantStatus import GiveawayParticipantStatus
from bot.models.giveawayParticipant import GiveawayParticipant


class GiveawayParticipantRepository:
    def __init__(self, session):
        self.session = session

    def findByGiveawayIdAndUserId(self, giveawayId: int, userId: int):
        return (
            self.session.query(GiveawayParticipant)
            .filter(GiveawayParticipant.giveaway_id == giveawayId)
            .filter(GiveawayParticipant.user_id == userId)
            .first()
        )

    def create(self, giveawayId: int, userId: int):
        participant = GiveawayParticipant(
            giveaway_id=giveawayId,
            user_id=userId,
            status=GiveawayParticipantStatus.ACTIVE.value,
        )

        self.session.add(participant)
        self.session.flush()

        return participant

    def createIfNotExists(self, giveawayId: int, userId: int):
        participant = self.findByGiveawayIdAndUserId(
            giveawayId=giveawayId,
            userId=userId,
        )

        if participant is not None:
            return participant

        return self.create(
            giveawayId=giveawayId,
            userId=userId,
        )

    def countActiveParticipants(self, giveawayId: int):
        return (
            self.session.query(GiveawayParticipant)
            .filter(GiveawayParticipant.giveaway_id == giveawayId)
            .filter(GiveawayParticipant.status == GiveawayParticipantStatus.ACTIVE.value)
            .count()
        )

    def findActiveParticipantsByGiveawayId(self, giveawayId: int):
        return (
            self.session.query(GiveawayParticipant)
            .filter(GiveawayParticipant.giveaway_id == giveawayId)
            .filter(GiveawayParticipant.status == GiveawayParticipantStatus.ACTIVE.value)
            .order_by(GiveawayParticipant.joined_at.asc(), GiveawayParticipant.id.asc())
            .all()
        )
