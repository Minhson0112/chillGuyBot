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

    def findByNormalizedPhrase(self, normalizedPhrase: str):
        return (
            self.session.query(WordChainPhraseMaster)
            .filter(WordChainPhraseMaster.normalized_phrase == normalizedPhrase)
            .first()
        )

    def upsertPhrase(
        self,
        phrase: str,
        normalizedPhrase: str,
        firstWord: str,
        lastWord: str,
    ):
        phraseMaster = self.findByNormalizedPhrase(normalizedPhrase)

        if phraseMaster is None:
            phraseMaster = WordChainPhraseMaster(
                phrase=phrase,
                normalized_phrase=normalizedPhrase,
                first_word=firstWord,
                last_word=lastWord,
                is_active=True,
            )
            self.session.add(phraseMaster)
            self.session.flush()
            return phraseMaster, True

        phraseMaster.phrase = phrase
        phraseMaster.first_word = firstWord
        phraseMaster.last_word = lastWord
        phraseMaster.is_active = True
        self.session.flush()

        return phraseMaster, False
