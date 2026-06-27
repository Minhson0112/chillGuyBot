from sqlalchemy import BigInteger, Boolean, Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from bot.config.database import Base


class FarmCowShed(Base):
    __tablename__ = "farm_cow_shed"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="farm cow shed id")
    farm_id = Column(
        BigInteger,
        ForeignKey("farm.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        comment="farm id"
    )
    cow_count = Column(Integer, nullable=False, default=0, comment="number of cows, max 1")

    cow_image_key = Column(String(255), nullable=True, comment="image key for cow")

    cow_x = Column(Integer, nullable=True, comment="x position of cow")
    cow_y = Column(Integer, nullable=True, comment="y position of cow")

    render_scale = Column(Float, nullable=False, default=1.0, comment="render scale for cow")

    last_fed_at = Column(DateTime, nullable=True, comment="last fed at")
    last_collected_milk_at = Column(DateTime, nullable=True, comment="last collected milk at")
    is_milk_ready_notified = Column(
        Boolean,
        nullable=False,
        default=False,
        comment="whether milk ready notification was sent",
    )
    is_hungry_notified = Column(
        Boolean,
        nullable=False,
        default=False,
        comment="whether hungry notification was sent",
    )

    created_at = Column(DateTime, nullable=False, server_default=func.now(), comment="created at")
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now(), comment="updated at")

    farm = relationship("Farm", back_populates="cowShed")
