from sqlalchemy import BigInteger ,Column, DateTime, ForeignKey, String, func
from sqlalchemy.dialects.mysql import BIGINT
from sqlalchemy.orm import relationship

from bot.config.database import Base


class WordGuessHistory(Base):
    __tablename__ = "word_guess_history"

    id = Column(BigInteger, primary_key=True, autoincrement=True, nullable=False)
    word_id = Column(
        BigInteger,
        ForeignKey("word.id"),
        nullable=False
    )
    guessed_by_user_id = Column(
        BigInteger,
        ForeignKey("member.user_id"),
        nullable=True
    )
    revealed_pattern = Column(String(255), nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now())

    word = relationship("Word")
    guessed_by_member = relationship("Member", foreign_keys=[guessed_by_user_id])