from sqlalchemy import BigInteger, Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from bot.config.database import Base


class FarmFishPond(Base):
    __tablename__ = "farm_fish_pond"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="farm fish pond id")
    farm_id = Column(
        BigInteger,
        ForeignKey("farm.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        comment="farm id"
    )

    last_fished_at = Column(DateTime, nullable=True, comment="last fished at")

    created_at = Column(DateTime, nullable=False, server_default=func.now(), comment="created at")
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now(), comment="updated at")

    farm = relationship("Farm", back_populates="fishPond")