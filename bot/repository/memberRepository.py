from bot.models.member import Member

class MemberRepository:
    def __init__(self, session):
        self.session = session