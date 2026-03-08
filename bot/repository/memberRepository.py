from bot.models.member import Member

class MemberRepository:
    def __init__(self, session):
        self.session = session

    def findByUserId(self, userId):
        return self.session.query(Member).filter(Member.user_id == userId).first()

    def create(self, memberData):
        member = Member(**memberData)
        self.session.add(member)
        self.session.flush()
        return member

    def update(self, member, memberData):
        for key, value in memberData.items():
            setattr(member, key, value)

        self.session.flush()
        return member

    def upsertByUserId(self, userId, memberData):
        member = self.findByUserId(userId)

        if member is None:
            return self.create(memberData)

        return self.update(member, memberData)