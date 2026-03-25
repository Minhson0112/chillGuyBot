from bot.models.chat import Chat
from sqlalchemy.orm import joinedload

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

    def createIfNotExists(self, userId):
        chat = self.findByUserId(userId)

        if chat is None:
            return self.create({
                "user_id": userId,
                "total_chat_count": 0,
                "level_chat_count": 0,
            })

        return chat

    def incrementChatCount(self, userId, totalIncrement, levelIncrement):
        chat = self.findByUserId(userId)

        if chat is None:
            chat = self.create({
                "user_id": userId,
                "total_chat_count": 0,
                "level_chat_count": 0,
            })

        chat.total_chat_count += totalIncrement
        chat.level_chat_count += levelIncrement

        self.session.flush()
        return chat

    def findTopChatMember(self) -> Chat | None:
        return (
            self.session.query(Chat)
            .options(joinedload(Chat.member))
            .order_by(Chat.total_chat_count.desc())
            .first()
        )