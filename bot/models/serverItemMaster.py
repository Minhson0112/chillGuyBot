from sqlalchemy import Boolean, Column, DateTime, Index, String
from sqlalchemy.dialects.mysql import BIGINT, INTEGER
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from bot.config.database import Base


class ServerItemMaster(Base):
    __tablename__ = "server_item_master"
    __table_args__ = (
        Index(
            "idx_server_item_master_type_active",
            "type",
            "is_active",
        ),
    )

    id = Column(BIGINT, primary_key=True, autoincrement=True, comment="server item id")
    name = Column(String(255), nullable=False, comment="server item name")
    type = Column(String(50), nullable=False, comment="server item type")
    price_cowoncy = Column(
        BIGINT(unsigned=True),
        nullable=False,
        default=0,
        comment="item price in cowoncy",
    )
    price_chill_coin = Column(
        BIGINT(unsigned=True),
        nullable=False,
        default=0,
        comment="item price in chill coin",
    )
    is_active = Column(Boolean, nullable=False, default=True, comment="whether item is active")
    icon_image_key = Column(String(255), nullable=False, comment="icon image key")
    intimacy_points = Column(
        INTEGER(unsigned=True),
        nullable=False,
        default=0,
        comment="intimacy points granted by item",
    )
    created_at = Column(DateTime, nullable=False, server_default=func.now(), comment="created at")

    inventories = relationship("ServerUserInventory", back_populates="item")
    giftHistories = relationship("ServerItemGiftHistory", back_populates="item")
