from bot.models.member import Member
from sqlalchemy import func
from sqlalchemy.orm import joinedload

class MemberRepository:
    def __init__(self, session):
        self.session = session

    def findByUserId(self, userId):
        return self.session.query(Member).filter(Member.user_id == userId).first()

    def findByUserIdWithChat(self, userId):
        return (
            self.session.query(Member)
            .options(joinedload(Member.chat))
            .filter(Member.user_id == userId)
            .first()
        )

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

    def countAllMembers(self) -> int:
        return self.session.query(func.count(Member.user_id)).scalar() or 0

    def updateIsPartner(self, userId, isPartner):
        member = self.findByUserId(userId)

        if member is None:
            return None

        member.is_partner = isPartner
        self.session.flush()
        return member
    
    def incrementCorrectWordGuessCount(self, userId):
        member = self.findByUserId(userId)

        if member is None:
            return None

        member.correct_word_guess_count += 1
        self.session.flush()
        return member
    
    def findTopCorrectWordGuessMembers(self, limit=10):
        return (
            self.session.query(Member)
            .filter(Member.correct_word_guess_count > 0)
            .order_by(Member.correct_word_guess_count.desc(), Member.user_id.asc())
            .limit(limit)
            .all()
        )
    