from sqlalchemy import BigInteger, Column, ForeignKey
from sqlalchemy.orm import relationship

from bot.config.database import Base


class Chat(Base):
    __tablename__ = "chat"

    user_id = Column(
        BigInteger,
        ForeignKey("member.user_id"),
        primary_key=True,
        comment="id discord",
    )
    total_chat_count = Column(BigInteger, nullable=False, default=0, comment="total chat in Chill Station")
    level_chat_count = Column(BigInteger, nullable=False, default=0, comment="total chat in Chill Station level channel")

    member = relationship("Member", back_populates="chat")