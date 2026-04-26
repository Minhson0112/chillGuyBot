from sqlalchemy import BigInteger, Boolean, Column, DateTime, ForeignKey, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from bot.config.database import Base


class ShopItem(Base):
    __tablename__ = "shop_items"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="shop item id")
    item_id = Column(
        BigInteger,
        ForeignKey("items.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        comment="item id"
    )
    buy_price = Column(Integer, nullable=False, default=0, comment="shop buy price")
    required_farm_level = Column(Integer, nullable=False, default=1, comment="required farm level to buy item")
    is_visible = Column(Boolean, nullable=False, default=True, comment="whether item is visible in shop")
    is_active = Column(Boolean, nullable=False, default=True, comment="whether item can be bought in shop")
    sort_order = Column(Integer, nullable=False, default=0, comment="shop display order")
    created_at = Column(DateTime, nullable=False, server_default=func.now(), comment="created at")
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now(), comment="updated at")

    item = relationship("Item", back_populates="shopItem")