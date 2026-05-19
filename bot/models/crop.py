from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from bot.config.database import Base


class Crop(Base):
    __tablename__ = "crops"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="crop id")
    code = Column(String(100), nullable=False, unique=True, comment="unique crop code")
    name = Column(String(255), nullable=False, comment="crop name")
    seed_item_id = Column(
        BigInteger,
        ForeignKey("items.id", ondelete="RESTRICT"),
        nullable=False,
        unique=True,
        comment="seed item id"
    )
    crop_item_id = Column(
        BigInteger,
        ForeignKey("items.id", ondelete="RESTRICT"),
        nullable=False,
        unique=True,
        comment="harvest item id"
    )
    harvest_quantity_per_plot = Column(Integer, nullable=False, default=1, comment="harvest quantity per plot")
    total_growth_seconds = Column(Integer, nullable=False, comment="total growth time in seconds")
    created_at = Column(DateTime, nullable=False, server_default=func.now(), comment="created at")
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now(), comment="updated at")

    growthStages = relationship(
        "CropGrowthStage",
        back_populates="crop",
        cascade="all, delete-orphan"
    )
    seedItem = relationship("Item", foreign_keys=[seed_item_id])
    cropItem = relationship("Item", foreign_keys=[crop_item_id])
    farmCropAreas = relationship("FarmCropArea", back_populates="crop")