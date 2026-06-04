from bot.models.memberDailyFortune import MemberDailyFortune


class MemberDailyFortuneRepository:
    def __init__(self, session):
        self.session = session

    def findByUserIdAndFortuneDate(
        self,
        userId: int,
        fortuneDate,
    ):
        return (
            self.session.query(MemberDailyFortune)
            .filter(MemberDailyFortune.user_id == userId)
            .filter(MemberDailyFortune.fortune_date == fortuneDate)
            .first()
        )

    def create(
        self,
        userId: int,
        fortuneDate,
        loveRate: int,
        luckRate: int,
        careerRate: int,
        description: str,
    ):
        dailyFortune = MemberDailyFortune(
            user_id=userId,
            fortune_date=fortuneDate,
            love_rate=loveRate,
            luck_rate=luckRate,
            career_rate=careerRate,
            description=description,
        )

        self.session.add(dailyFortune)
        self.session.flush()

        return dailyFortune
