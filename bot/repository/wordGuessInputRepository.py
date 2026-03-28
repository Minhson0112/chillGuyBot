from bot.models.wordGuessInput import WordGuessInput

class WordGuessInputRepository:
    def __init__(self, session):
        self.session = session

    def findAllGuessWords(self):
        rows = self.session.query(WordGuessInput.guess_word).all()
        return [row[0] for row in rows]
    