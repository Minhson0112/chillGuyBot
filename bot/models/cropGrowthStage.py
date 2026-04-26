from sqlalchemy import BigInteger, Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from bot.config.database import Base


class CropGrowthStage(Base):
    __tablename__ = "crop_growth_stages"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="crop growth stage id")
    crop_id = Column(
        BigInteger,
        ForeignKey("crops.id", ondelete="CASCADE"),
        nullable=False,
        comment="crop id"
    )
    stage_no = Column(Integer, nullable=False, comment="growth stage number")
    stage_start_seconds = Column(Integer, nullable=False, comment="elapsed seconds from planted time to reach this stage")
    image_key = Column(String(255), nullable=False, comment="image key for this crop stage")
    render_scale = Column(Float, nullable=False, default=1.0, comment="render scale for this stage image")
    render_offset_y = Column(Integer, nullable=False, default=0, comment="vertical offset when rendering this stage image")
    created_at = Column(DateTime, nullable=False, server_default=func.now(), comment="created at")
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now(), comment="updated at")

    crop = relationship("Crop", back_populates="growthStages")