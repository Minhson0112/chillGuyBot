from sqlalchemy import BigInteger, Boolean, Column, DateTime, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from bot.config.database import Base


class BaseSkinMaster(Base):
    __tablename__ = "base_skin_master"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="base skin id")
    code = Column(String(100), nullable=False, unique=True, comment="unique base skin code")
    name = Column(String(255), nullable=False, comment="base skin name")
    base_image_key = Column(String(255), nullable=False, unique=True, comment="farm base image key")
    description = Column(String(500), nullable=True, comment="base skin description")
    buy_price = Column(Integer, nullable=False, default=0, comment="buy price in chill coin")
    required_farm_level = Column(Integer, nullable=False, default=1, comment="required farm level")
    is_active = Column(Boolean, nullable=False, default=True, comment="is active")
    created_at = Column(DateTime, nullable=False, server_default=func.now(), comment="created at")
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now(), comment="updated at")

    memberInventories = relationship(
        "MemberBaseSkinInventory",
        back_populates="baseSkin",
    )
