from sqlalchemy import BigInteger, Boolean, Column, DateTime, Float, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from bot.config.database import Base


class Item(Base):
    __tablename__ = "items"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="item id")
    code = Column(String(100), nullable=False, unique=True, comment="unique item code")
    name = Column(String(255), nullable=False, comment="item name")
    type_code = Column(String(50), nullable=False, index=True, comment="item type code")
    icon_image_key = Column(String(255), nullable=False, comment="icon image key")
    description = Column(String(500), nullable=True, comment="item description")

    render_scale = Column(Float, nullable=False, default=1.0, comment="scale when rendering in game")
    render_offset_y = Column(Integer, nullable=False, default=0, comment="vertical offset when rendering")

    sell_price = Column(Integer, nullable=False, default=0, comment="sell price")
    is_sellable = Column(Boolean, nullable=False, default=True, comment="can sell")
    is_usable = Column(Boolean, nullable=False, default=False, comment="can use")
    is_active = Column(Boolean, nullable=False, default=True, comment="is active")

    created_at = Column(DateTime, nullable=False, server_default=func.now(), comment="created at")
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now(), comment="updated at")

    shopItem = relationship("ShopItem", back_populates="item", uselist=False, cascade="all, delete-orphan")
    inventories = relationship("UserInventory", back_populates="item", cascade="all, delete-orphan")