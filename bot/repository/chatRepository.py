from bot.models.chat import Chat

class ChatRepository:
    def __init__(self, session):
        self.session = session

    def findByUserId(self, userId):
        return self.session.query(Chat).filter(Chat.user_id == userId).first()

    def create(self, chatData):
        chat = Chat(**chatData)
        self.session.add(chat)
        self.session.flush()
        return chat