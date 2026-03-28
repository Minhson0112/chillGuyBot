from sqlalchemy.orm import joinedload

from bot.models.wordGuessHistory import WordGuessHistory


class WordGuessHistoryRepository:
    def __init__(self, session):
        self.session = session

    def findCurrentGuessingWord(self):
        return (
            self.session.query(WordGuessHistory)
            .options(joinedload(WordGuessHistory.word))
            .filter(WordGuessHistory.guessed_by_user_id.is_(None))
            .first()
        )

    def create(self, wordGuessHistoryData):
        wordGuessHistory = WordGuessHistory(**wordGuessHistoryData)
        self.session.add(wordGuessHistory)
        self.session.flush()
        return wordGuessHistory

    def updateGuessedByUserId(self, historyId, guessedByUserId):
        wordGuessHistory = (
            self.session.query(WordGuessHistory)
            .filter(WordGuessHistory.id == historyId)
            .first()
        )

        if wordGuessHistory is None:
            return None

        wordGuessHistory.guessed_by_user_id = guessedByUserId
        self.session.flush()
        return wordGuessHistory