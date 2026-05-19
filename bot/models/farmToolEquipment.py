from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, String, text
from sqlalchemy.orm import relationship

from bot.config.database import Base


class FarmToolEquipment(Base):
    __tablename__ = "farm_tool_equipment"

    id = Column(BigInteger, primary_key=True, autoincrement=True)

    farm_id = Column(
        BigInteger,
        ForeignKey("farm.id", ondelete="CASCADE"),
        nullable=False,
    )

    tool_type = Column(String(50), nullable=False)

    user_tool_id = Column(
        BigInteger,
        ForeignKey("user_tools.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )

    equipped_at = Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    created_at = Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(
        DateTime,
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
        server_onupdate=text("CURRENT_TIMESTAMP"),
    )

    farm = relationship("Farm")
    user_tool = relationship("UserTool", back_populates="farm_tool_equipment")