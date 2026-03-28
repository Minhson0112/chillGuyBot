from sqlalchemy import Column, String, BigInteger

from bot.config.database import Base

class WordGuessInput(Base):
    __tablename__ = "word_guess_input"

    id = Column(BigInteger, primary_key=True, autoincrement=True, nullable=False)
    guess_word = Column(String(255), nullable=False, unique=True)
    