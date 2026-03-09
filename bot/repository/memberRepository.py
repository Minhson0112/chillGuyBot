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

    def upsertOnJoin(self, userId, memberData):
        member = self.findByUserId(userId)

        if member is None:
            return self.create(memberData)

        member.global_name = memberData["global_name"]
        member.username = memberData["username"]
        member.nick = memberData["nick"]
        member.joined_at = memberData["joined_at"]
        member.leave_at = None
        member.is_bot = memberData["is_bot"]
        member.join_count += 1

        self.session.flush()
        return member

    def updateLeaveAt(self, userId, leaveAt):
        member = self.findByUserId(userId)

        if member is None:
            return None

        member.leave_at = leaveAt

        self.session.flush()
        return member

    def incrementWarningCount(self, userId):
        member = self.findByUserId(userId)

        if member is None:
            return None

        member.warning_count += 1
        self.session.flush()
        return member

    def resetWarningCount(self, userId):
        member = self.findByUserId(userId)

        if member is None:
            return None

        member.warning_count = 0
        self.session.flush()
        return member