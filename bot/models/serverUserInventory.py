from sqlalchemy import Column, DateTime, ForeignKey, Index, UniqueConstraint
from sqlalchemy.dialects.mysql import BIGINT
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from bot.config.database import Base


class ServerUserInventory(Base):
    __tablename__ = "server_user_inventory"
    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "item_id",
            name="uq_server_user_inventory_user_item",
        ),
        Index("idx_server_user_inventory_item_id", "item_id"),
    )

    id = Column(BIGINT, primary_key=True, autoincrement=True, comment="server user inventory id")
    user_id = Column(
        BIGINT(unsigned=True),
        ForeignKey("member.user_id", ondelete="CASCADE"),
        nullable=False,
        comment="discord user id",
    )
    item_id = Column(
        BIGINT,
        ForeignKey("server_item_master.id", ondelete="RESTRICT"),
        nullable=False,
        comment="server item id",
    )
    quantity = Column(
        BIGINT(unsigned=True),
        nullable=False,
        default=0,
        comment="item quantity",
    )
    created_at = Column(DateTime, nullable=False, server_default=func.now(), comment="created at")
    updated_at = Column(
        DateTime,
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
        comment="updated at",
    )

    member = relationship("Member")
    item = relationship("ServerItemMaster", back_populates="inventories")
