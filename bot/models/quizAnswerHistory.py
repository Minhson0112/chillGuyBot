from sqlalchemy import CheckConstraint, Column, DateTime, ForeignKey, Index, String
from sqlalchemy.dialects.mysql import BIGINT
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from bot.config.database import Base


class QuizAnswerHistory(Base):
    __tablename__ = "quiz_answer_history"
    __table_args__ = (
        Index("idx_quiz_answer_history_user_created_at", "user_id", "created_at"),
        Index("idx_quiz_answer_history_difficulty_created_at", "difficulty", "created_at"),
        CheckConstraint(
            "difficulty IN ('easy', 'medium', 'hard')",
            name="chk_quiz_answer_history_difficulty",
        ),
    )

    id = Column(BIGINT, primary_key=True, autoincrement=True, comment="quiz answer history id")
    user_id = Column(
        BIGINT(unsigned=True),
        ForeignKey("member.user_id", ondelete="RESTRICT"),
        nullable=False,
        comment="discord user id",
    )
    difficulty = Column(
        String(20),
        nullable=False,
        comment="question difficulty: easy, medium, hard",
    )
    created_at = Column(DateTime, nullable=False, server_default=func.now(), comment="created at")

    member = relationship("Member", back_populates="quizAnswerHistories")
