from sqlalchemy import CheckConstraint, Column, DateTime, ForeignKey, Index
from sqlalchemy.dialects.mysql import BIGINT
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from bot.config.database import Base


class ServerItemGiftHistory(Base):
    __tablename__ = "server_item_gift_histories"
    __table_args__ = (
        Index(
            "idx_server_item_gift_histories_giver_created_at",
            "giver_user_id",
            "created_at",
        ),
        Index(
            "idx_server_item_gift_histories_receiver_created_at",
            "receiver_user_id",
            "created_at",
        ),
        Index("idx_server_item_gift_histories_item_id", "item_id"),
        CheckConstraint(
            "giver_user_id <> receiver_user_id",
            name="chk_server_item_gift_histories_distinct_users",
        ),
        CheckConstraint(
            "quantity > 0",
            name="chk_server_item_gift_histories_quantity",
        ),
    )

    id = Column(BIGINT, primary_key=True, autoincrement=True, comment="server item gift history id")
    giver_user_id = Column(
        BIGINT(unsigned=True),
        ForeignKey("member.user_id", ondelete="RESTRICT"),
        nullable=False,
        comment="discord user id of gift giver",
    )
    receiver_user_id = Column(
        BIGINT(unsigned=True),
        ForeignKey("member.user_id", ondelete="RESTRICT"),
        nullable=False,
        comment="discord user id of gift receiver",
    )
    item_id = Column(
        BIGINT,
        ForeignKey("server_item_master.id", ondelete="RESTRICT"),
        nullable=False,
        comment="gifted server item id",
    )
    quantity = Column(
        BIGINT(unsigned=True),
        nullable=False,
        comment="gifted item quantity",
    )
    created_at = Column(DateTime, nullable=False, server_default=func.now(), comment="created at")

    giverMember = relationship("Member", foreign_keys=[giver_user_id])
    receiverMember = relationship("Member", foreign_keys=[receiver_user_id])
    item = relationship("ServerItemMaster", back_populates="giftHistories")
