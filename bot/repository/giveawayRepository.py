from bot.enums.giveawayStatus import GiveawayStatus
from bot.models.giveaway import Giveaway


class GiveawayRepository:
    def __init__(self, session):
        self.session = session

    def create(
        self,
        title: str,
        giveawayType: str,
        winnerCount: int,
        durationSeconds: int,
        drawAt,
        channelId: int,
        createdByUserId: int,
        rewardChillCoin: int | None = None,
        rewardCowoncy: int | None = None,
        rewardVnd: int | None = None,
        rewardText: str | None = None,
    ):
        giveaway = Giveaway(
            title=title,
            type=giveawayType,
            winner_count=winnerCount,
            reward_chill_coin=rewardChillCoin,
            reward_cowoncy=rewardCowoncy,
            reward_vnd=rewardVnd,
            reward_text=rewardText,
            status=GiveawayStatus.ACTIVE.value,
            duration_seconds=durationSeconds,
            draw_at=drawAt,
            channel_id=channelId,
            created_by_user_id=createdByUserId,
        )

        self.session.add(giveaway)
        self.session.flush()

        return giveaway

    def findById(self, giveawayId: int):
        return (
            self.session.query(Giveaway)
            .filter(Giveaway.id == giveawayId)
            .first()
        )

    def findActiveGiveawaysWithMessage(self):
        return (
            self.session.query(Giveaway)
            .filter(Giveaway.status == GiveawayStatus.ACTIVE.value)
            .filter(Giveaway.message_id.isnot(None))
            .all()
        )

    def updateMessageId(self, giveawayId: int, messageId: int):
        giveaway = self.findById(giveawayId)

        if giveaway is None:
            return None

        giveaway.message_id = messageId
        self.session.flush()

        return giveaway
