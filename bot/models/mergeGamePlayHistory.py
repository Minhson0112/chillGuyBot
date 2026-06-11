from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from bot.config.database import Base


class MergeGamePlayHistory(Base):
    __tablename__ = "merge_game_play_history"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="merge game play history id")

    user_id = Column(
        BigInteger,
        ForeignKey("member.user_id", ondelete="CASCADE"),
        nullable=False,
        comment="discord user id",
    )

    score = Column(Integer, nullable=False, comment="game score")
    sun_time = Column(BigInteger, nullable=True, comment="milliseconds until creating sun")

    created_at = Column(DateTime, nullable=False, server_default=func.now(), comment="created at")

    member = relationship("Member", back_populates="mergeGamePlayHistories")
