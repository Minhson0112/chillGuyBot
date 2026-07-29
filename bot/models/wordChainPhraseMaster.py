from sqlalchemy import Boolean, Column, DateTime, Index, String, UniqueConstraint
from sqlalchemy.dialects.mysql import BIGINT
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from bot.config.database import Base


class WordChainPhraseMaster(Base):
    __tablename__ = "word_chain_phrase_master"
    __table_args__ = (
        UniqueConstraint(
            "normalized_phrase",
            name="uq_word_chain_phrase_master_normalized_phrase",
        ),
        Index("idx_word_chain_phrase_master_first_word", "first_word"),
        Index("idx_word_chain_phrase_master_last_word", "last_word"),
        Index("idx_word_chain_phrase_master_is_active", "is_active"),
    )

    id = Column(
        BIGINT,
        primary_key=True,
        autoincrement=True,
        comment="word chain phrase master id",
    )
    phrase = Column(String(100), nullable=False, comment="display phrase")
    normalized_phrase = Column(
        String(100),
        nullable=False,
        comment="normalized phrase used for lookup",
    )
    first_word = Column(String(50), nullable=False, comment="first word in phrase")
    last_word = Column(String(50), nullable=False, comment="last word in phrase")
    is_active = Column(
        Boolean,
        nullable=False,
        default=True,
        comment="whether phrase is active",
    )
    created_at = Column(DateTime, nullable=False, server_default=func.now(), comment="created at")
    updated_at = Column(
        DateTime,
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
        comment="updated at",
    )

    winHistories = relationship("WordChainWinHistory", back_populates="phraseMaster")
    gameStates = relationship("WordChainGameState", back_populates="lastPhraseMaster")
