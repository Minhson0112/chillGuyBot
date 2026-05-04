from sqlalchemy.orm import joinedload

from bot.models.giftcode import Giftcode
from bot.models.giftcodeReward import GiftcodeReward


class GiftcodeRepository:
    def __init__(self, session):
        self.session = session

    def findByCodeWithRewards(self, code: str):
        return (
            self.session.query(Giftcode)
            .options(
                joinedload(Giftcode.rewards)
                .joinedload(GiftcodeReward.item)
            )
            .filter(Giftcode.code == code)
            .first()
        )