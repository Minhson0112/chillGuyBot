from sqlalchemy import Column, String, BigInteger

from bot.config.database import Base


class Word(Base):
    __tablename__ = "word"

    id = Column(BigInteger, primary_key=True, autoincrement=True, nullable=False)
    key_word = Column(String(255), nullable=False, unique=True)