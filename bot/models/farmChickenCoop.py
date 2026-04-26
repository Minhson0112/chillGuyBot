from sqlalchemy import BigInteger, Column, DateTime, Float, ForeignKey, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from bot.config.database import Base


class FarmChickenCoop(Base):
    __tablename__ = "farm_chicken_coop"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="farm chicken coop id")
    farm_id = Column(
        BigInteger,
        ForeignKey("farm.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        comment="farm id"
    )
    chicken_count = Column(Integer, nullable=False, default=0, comment="number of chickens, max 2")

    chicken_1_x = Column(Integer, nullable=True, comment="x position of chicken 1")
    chicken_1_y = Column(Integer, nullable=True, comment="y position of chicken 1")
    chicken_2_x = Column(Integer, nullable=True, comment="x position of chicken 2")
    chicken_2_y = Column(Integer, nullable=True, comment="y position of chicken 2")

    render_scale = Column(Float, nullable=False, default=1.0, comment="render scale for chickens")
    last_fed_at = Column(DateTime, nullable=True, comment="last fed at")
    last_collected_egg_at = Column(DateTime, nullable=True, comment="last collected egg at")

    created_at = Column(DateTime, nullable=False, server_default=func.now(), comment="created at")
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now(), comment="updated at")

    farm = relationship("Farm", back_populates="chickenCoop")