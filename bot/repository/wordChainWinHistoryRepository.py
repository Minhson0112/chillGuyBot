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
