from datetime import datetime

from sqlalchemy import desc, func

from bot.models.member import Member
from bot.models.wordChainWinHistory import WordChainWinHistory


class WordChainWinHistoryRepository:
    def __init__(self, session):
        self.session = session

    def create(self, userId: int, phraseMasterId: int):
        winHistory = WordChainWinHistory(
            user_id=userId,
            phrase_master_id=phraseMasterId,
        )

        self.session.add(winHistory)
        self.session.flush()

        return winHistory

    def findLatestPhraseMasterIds(self, limit: int):
        rows = (
            self.session.query(WordChainWinHistory.phrase_master_id)
            .order_by(WordChainWinHistory.created_at.desc(), WordChainWinHistory.id.desc())
            .limit(limit)
            .all()
        )

        return [row[0] for row in rows]

    def findTopWinMembersByMonth(
        self,
        year: int,
        month: int,
        limit: int = 5,
    ):
        startAt, endAt = self.getMonthRange(year, month)
        winCount = func.count(WordChainWinHistory.id).label("win_count")

        return (
            self.session.query(
                Member.user_id,
                Member.global_name,
                Member.username,
                Member.nick,
                winCount,
            )
            .join(Member, Member.user_id == WordChainWinHistory.user_id)
            .filter(WordChainWinHistory.created_at >= startAt)
            .filter(WordChainWinHistory.created_at < endAt)
            .group_by(
                Member.user_id,
                Member.global_name,
                Member.username,
                Member.nick,
            )
            .order_by(desc(winCount))
            .limit(limit)
            .all()
        )

    def getMonthRange(self, year: int, month: int):
        startAt = datetime(year, month, 1)

        if month == 12:
            endAt = datetime(year + 1, 1, 1)
        else:
            endAt = datetime(year, month + 1, 1)

        return startAt, endAt
