from sqlalchemy import CheckConstraint, Column, DateTime, ForeignKey, Index, String
from sqlalchemy.dialects.mysql import BIGINT, TINYINT
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from bot.config.database import Base


class WordChainGameState(Base):
    __tablename__ = "word_chain_game_state"
    __table_args__ = (
        Index(
            "idx_word_chain_game_state_last_phrase_master_id",
            "last_phrase_master_id",
        ),
        Index("idx_word_chain_game_state_last_user_id", "last_user_id"),
        CheckConstraint("id = 1", name="chk_word_chain_game_state_single_row"),
    )

    id = Column(
        TINYINT(unsigned=True),
        primary_key=True,
        comment="single word chain game state id",
    )
    last_phrase_master_id = Column(
        BIGINT,
        ForeignKey("word_chain_phrase_master.id", ondelete="RESTRICT"),
        nullable=True,
        comment="last phrase master id used in current chain",
    )
    last_word = Column(
        String(50, collation="utf8mb4_bin"),
        nullable=True,
        comment="last word players must connect from",
    )
    last_user_id = Column(
        BIGINT(unsigned=True),
        ForeignKey("member.user_id", ondelete="SET NULL"),
        nullable=True,
        comment="discord user id who submitted the last phrase",
    )
    updated_at = Column(
        DateTime,
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
        comment="updated at",
    )

    lastPhraseMaster = relationship("WordChainPhraseMaster", back_populates="gameStates")
    lastUser = relationship("Member", back_populates="wordChainGameStates")
