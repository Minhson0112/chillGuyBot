from sqlalchemy import BigInteger, Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from bot.config.database import Base


class Farm(Base):
    __tablename__ = "farm"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="farm id")
    user_id = Column(
        BigInteger,
        ForeignKey("member.user_id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        comment="owner discord user id"
    )
    farm_level = Column(Integer, nullable=False, default=1, comment="farm level")
    farm_exp = Column(Integer, nullable=False, default=0, comment="farm experience")
    base_image_key = Column(String(255), nullable=True, default="base", comment="base image key for farm rendering")
    is_train_event = Column(Boolean, nullable=False, default=False, comment="whether train event is active in farm")
    created_at = Column(DateTime, nullable=False, server_default=func.now(), comment="created at")
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now(), comment="updated at")

    member = relationship("Member", back_populates="farm")
    cropArea = relationship("FarmCropArea", back_populates="farm", uselist=False, cascade="all, delete-orphan")
    chickenCoop = relationship("FarmChickenCoop", back_populates="farm", uselist=False, cascade="all, delete-orphan")
    cowShed = relationship("FarmCowShed", back_populates="farm", uselist=False, cascade="all, delete-orphan")
    fishPond = relationship("FarmFishPond", back_populates="farm", uselist=False, cascade="all, delete-orphan")