from sqlalchemy.sql import func

from bot.models.word import Word


class WordRepository:
    def __init__(self, session):
        self.session = session

    def findById(self, wordId):
        return self.session.query(Word).filter(Word.id == wordId).first()

    def findByKeyWord(self, keyWord):
        return self.session.query(Word).filter(Word.key_word == keyWord).first()

    def create(self, wordData):
        word = Word(**wordData)
        self.session.add(word)
        self.session.flush()
        return word

    def findRandomWord(self):
        return self.session.query(Word).order_by(func.rand()).first()
    
    def findAllKeyWords(self):
        rows = self.session.query(Word.key_word).all()
        return [row[0] for row in rows]