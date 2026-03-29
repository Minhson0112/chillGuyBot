from sqlalchemy import BigInteger, Boolean, Column, DateTime, ForeignKey, String, text
from sqlalchemy.orm import relationship

from bot.config.database import Base


class AutoResponder(Base):
    __tablename__ = "auto_responder"

    id_auto_responder = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(
        BigInteger,
        ForeignKey("member.user_id"),
        nullable=False,
        comment="member who created this auto responder",
    )
    msg_key = Column(
        String(100),
        nullable=False,
        unique=True,
        comment="trigger key",
    )
    is_global = Column(
        Boolean,
        nullable=False,
        default=False,
        comment="whether other members can use this key",
    )
    is_exact_match = Column(
        Boolean,
        nullable=False,
        default=True,
        comment="true: exact match, false: contains match",
    )
    msg_link = Column(
        String(500),
        nullable=False,
        comment="discord message link used as template",
    )
    deleted_at = Column(
        DateTime,
        nullable=True,
        comment="soft delete timestamp",
    )
    created_at = Column(
        DateTime,
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
        comment="created at",
    )
    updated_at = Column(
        DateTime,
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
        server_onupdate=text("CURRENT_TIMESTAMP"),
        comment="updated at",
    )

    member = relationship("Member")