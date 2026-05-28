from datetime import datetime, timezone

from bot.enums.giveawayWinnerDisqualifiedReason import GiveawayWinnerDisqualifiedReason
from bot.enums.giveawayWinnerStatus import GiveawayWinnerStatus
from bot.models.giveawayWinner import GiveawayWinner


class GiveawayWinnerRepository:
    def __init__(self, session):
        self.session = session

    def create(
        self,
        giveawayId: int,
        userId: int,
        slotNumber: int,
        drawRound: int = 1,
        rerolledFromWinnerId: int | None = None,
    ):
        winner = GiveawayWinner(
            giveaway_id=giveawayId,
            user_id=userId,
            draw_round=drawRound,
            slot_number=slotNumber,
            current_slot_number=slotNumber,
            status=GiveawayWinnerStatus.SELECTED.value,
            rerolled_from_winner_id=rerolledFromWinnerId,
        )

        self.session.add(winner)
        self.session.flush()

        return winner

    def findById(self, winnerId: int):
        return (
            self.session.query(GiveawayWinner)
            .filter(GiveawayWinner.id == winnerId)
            .first()
        )

    def findCurrentWinnersByGiveawayId(self, giveawayId: int):
        return (
            self.session.query(GiveawayWinner)
            .filter(GiveawayWinner.giveaway_id == giveawayId)
            .filter(GiveawayWinner.current_slot_number.isnot(None))
            .order_by(GiveawayWinner.current_slot_number.asc())
            .all()
        )

    def findWinnerUserIdsByGiveawayId(self, giveawayId: int):
        rows = (
            self.session.query(GiveawayWinner.user_id)
            .filter(GiveawayWinner.giveaway_id == giveawayId)
            .all()
        )

        return {row[0] for row in rows}

    def findAllCurrentWinners(self):
        return (
            self.session.query(GiveawayWinner)
            .filter(GiveawayWinner.current_slot_number.isnot(None))
            .order_by(GiveawayWinner.giveaway_id.asc(), GiveawayWinner.current_slot_number.asc())
            .all()
        )

    def markRerolled(self, winner):
        winner.status = GiveawayWinnerStatus.REROLLED.value
        winner.current_slot_number = None
        winner.disqualified_reason = GiveawayWinnerDisqualifiedReason.MANUAL_REROLL.value
        winner.disqualified_at = datetime.now(timezone.utc).replace(tzinfo=None)

        self.session.flush()

        return winner
