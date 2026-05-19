from sqlalchemy import BigInteger, Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from bot.config.database import Base


class FarmCropArea(Base):
    __tablename__ = "farm_crop_area"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="farm crop area id")
    farm_id = Column(
        BigInteger,
        ForeignKey("farm.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        comment="farm id"
    )
    unlocked_plot_count = Column(Integer, nullable=False, default=1, comment="number of unlocked plots")
    crop_id = Column(
        BigInteger,
        ForeignKey("crops.id", ondelete="SET NULL"),
        nullable=True,
        comment="current planted crop id"
    )
    planted_at = Column(DateTime, nullable=True, comment="planted at")
    harvestable_at = Column(DateTime, nullable=True, comment="harvestable at")

    last_watered_at = Column(DateTime, nullable=True, comment="last watered at")
    last_pest_removed_at = Column(DateTime, nullable=True, comment="last pest removed at")

    is_dry = Column(Boolean, nullable=False, default=False, comment="whether crop area is dry")
    is_pest_infected = Column(Boolean, nullable=False, default=False, comment="whether crop area has pest infection")

    dryness_started_at = Column(DateTime, nullable=True, comment="when dryness started")
    pest_started_at = Column(DateTime, nullable=True, comment="when pest infection started")

    total_dry_seconds = Column(Integer, nullable=False, default=0, comment="total dry duration in seconds")
    total_pest_seconds = Column(Integer, nullable=False, default=0, comment="total pest duration in seconds")

    status = Column(String(50), nullable=False, default="idle", comment="crop area status")

    created_at = Column(DateTime, nullable=False, server_default=func.now(), comment="created at")
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now(), comment="updated at")

    farm = relationship("Farm", back_populates="cropArea")
    crop = relationship("Crop", back_populates="farmCropAreas")