import asyncio
import os
from datetime import datetime
from PIL import Image

from bot.config.database import getDbSession
from bot.models.member import Member
from bot.models.quizAnswerHistory import QuizAnswerHistory
from bot.repository.quizAnswerHistoryRepository import QuizAnswerHistoryRepository
from bot.services.asset.assetImageService import assetImageService
from bot.services.quiz.memberQuizRankingImageService import MemberQuizRankingImageService


class MockGuild:
    def __init__(self):
        self.id = 123456789
        self.name = "Test Guild"

    def get_member(self, user_id):
        class MockMember:
            def __init__(self, uid):
                self.id = uid
                self.display_name = f"User_{uid}"
                self.mention = f"<@{uid}>"
        return MockMember(user_id)


class MockBot:
    def __init__(self):
        pass

    async def fetch_user(self, user_id):
        class MockUser:
            def __init__(self, uid):
                self.id = uid
                self.display_name = f"User_{uid}"
        return MockUser(user_id)


async def main():
    # Preload assets for assetImageService
    assetImageService.preloadAssets()

    print("Connecting to database...")
    with getDbSession() as session:
        # Get some existing members
        members = session.query(Member).limit(3).all()
        if not members:
            print("No members found in the database. Please make sure loadmember has been run.")
            return

        print(f"Found {len(members)} members in database:")
        for m in members:
            print(f"  - {m.user_id}")

        # Clean old test entries for current month to start clean
        now = datetime.now()
        session.query(QuizAnswerHistory).filter(
            QuizAnswerHistory.user_id.in_([m.user_id for m in members])
        ).delete(synchronize_session=False)
        session.commit()

        # Insert some mock quiz histories
        # Member 0 gets: 1 hard (30 pts), 1 medium (20 pts), 1 easy (10 pts) -> Total 60 pts
        # Member 1 gets: 2 medium (40 pts) -> Total 40 pts
        # Member 2 gets: 2 easy (20 pts) -> Total 20 pts
        quiz_repo = QuizAnswerHistoryRepository(session)
        
        # Member 0
        quiz_repo.create(members[0].user_id, "hard")
        quiz_repo.create(members[0].user_id, "medium")
        quiz_repo.create(members[0].user_id, "easy")
        
        # Member 1
        if len(members) > 1:
            quiz_repo.create(members[1].user_id, "medium")
            quiz_repo.create(members[1].user_id, "medium")
            
        # Member 2
        if len(members) > 2:
            quiz_repo.create(members[2].user_id, "easy")
            quiz_repo.create(members[2].user_id, "easy")

        session.commit()
        print("Inserted mock quiz answers.")

        # Query rankings
        top_members = quiz_repo.findTopQuizMembersByMonth(now.year, now.month, 10)
        print("\nLeaderboard Query Result:")
        for idx, (m, score) in enumerate(top_members):
            print(f"Rank {idx+1}: User {m.user_id} - Score: {score}")

        # Render ranking image
        bot = MockBot()
        guild = MockGuild()
        image_service = MemberQuizRankingImageService(bot)
        
        image_buffer = await image_service.buildRankingImage(top_members, guild)
        
        # Save image to file
        output_path = "bot/scratch/quiz_leaderboard_test.png"
        with open(output_path, "wb") as f:
            f.write(image_buffer.getvalue())
        print(f"\nRendered leaderboard image successfully saved to {output_path}")


if __name__ == "__main__":
    asyncio.run(main())
