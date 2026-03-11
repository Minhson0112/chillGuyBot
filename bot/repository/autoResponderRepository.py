from bot.models.autoResponder import AutoResponder

class AutoResponderRepository:
    def __init__(self, session):
        self.session = session

    def create(self, autoResponderData):
        autoResponder = AutoResponder(**autoResponderData)
        self.session.add(autoResponder)
        self.session.flush()
        return autoResponder

    def findByMsgKey(self, msgKey):
        return self.session.query(AutoResponder).filter(
            AutoResponder.msg_key == msgKey,
            AutoResponder.deleted_at.is_(None)
        ).first()

    def getAll(self):
        return self.session.query(AutoResponder).all()

    def delete(self, autoResponder):
        self.session.delete(autoResponder)
        self.session.flush()