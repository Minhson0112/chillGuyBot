from sqlalchemy import distinct
from sqlalchemy.sql import func

from bot.models.wordChainPhraseMaster import WordChainPhraseMaster


class WordChainPhraseMasterRepository:
    def __init__(self, session):
        self.session = session

    def findAllActive(self):
        return (
            self.session.query(WordChainPhraseMaster)
            .filter(WordChainPhraseMaster.is_active.is_(True))
            .order_by(WordChainPhraseMaster.id)
            .all()
        )

    def findRandomFirstWord(self):
        row = (
            self.session.query(distinct(WordChainPhraseMaster.first_word))
            .filter(WordChainPhraseMaster.is_active.is_(True))
            .order_by(func.rand())
            .first()
        )

        if row is None:
            return None

        return row[0]
