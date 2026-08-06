from bot.models.quizAnswerHistory import QuizAnswerHistory


class QuizAnswerHistoryRepository:
    def __init__(self, session):
        self.session = session

    def create(self, userId: int, difficulty: str):
        quizAnswerHistory = QuizAnswerHistory(
            user_id=userId,
            difficulty=difficulty,
        )

        self.session.add(quizAnswerHistory)
        self.session.flush()

        return quizAnswerHistory

    def findTopQuizMembersByMonth(self, year: int, month: int, limit: int = 10):
        from sqlalchemy import case, func, extract
        from bot.models.member import Member

        score_expr = func.sum(
            case(
                (QuizAnswerHistory.difficulty == "easy", 10),
                (QuizAnswerHistory.difficulty == "medium", 20),
                (QuizAnswerHistory.difficulty == "hard", 30),
                else_=0
            )
        ).label("score")

        return (
            self.session.query(
                Member,
                score_expr
            )
            .join(QuizAnswerHistory, Member.user_id == QuizAnswerHistory.user_id)
            .filter(extract('year', QuizAnswerHistory.created_at) == year)
            .filter(extract('month', QuizAnswerHistory.created_at) == month)
            .group_by(QuizAnswerHistory.user_id)
            .order_by(score_expr.desc())
            .limit(limit)
            .all()
        )
