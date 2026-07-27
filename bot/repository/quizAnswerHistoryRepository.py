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
