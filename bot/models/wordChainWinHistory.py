from sqlalchemy import Column, DateTime, ForeignKey, Index
from sqlalchemy.dialects.mysql import BIGINT
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from bot.config.database import Base


class WordChainWinHistory(Base):
    __tablename__ = "word_chain_win_history"
    __table_args__ = (
        Index("idx_word_chain_win_history_user_id", "user_id"),
        Index("idx_word_chain_win_history_phrase_master_id", "phrase_master_id"),
        Index("idx_word_chain_win_history_created_at", "created_at"),
    )

    id = Column(
        BIGINT,
        primary_key=True,
        autoincrement=True,
        comment="word chain win history id",
    )
    user_id = Column(
        BIGINT(unsigned=True),
        ForeignKey("member.user_id", ondelete="RESTRICT"),
        nullable=False,
        comment="discord user id who won",
    )
    phrase_master_id = Column(
        BIGINT,
        ForeignKey("word_chain_phrase_master.id", ondelete="RESTRICT"),
        nullable=False,
        comment="phrase master id used to win",
    )
    created_at = Column(DateTime, nullable=False, server_default=func.now(), comment="created at")

    member = relationship("Member", back_populates="wordChainWinHistories")
    phraseMaster = relationship("WordChainPhraseMaster", back_populates="winHistories")
