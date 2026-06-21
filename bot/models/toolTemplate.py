from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, Integer, Numeric, String, text
from sqlalchemy.orm import relationship

from bot.config.database import Base


class ToolTemplate(Base):
    __tablename__ = "tool_templates"

    id = Column(BigInteger, primary_key=True, autoincrement=True)

    item_id = Column(
        BigInteger,
        ForeignKey("items.id", ondelete="RESTRICT"),
        nullable=False,
    )

    tool_type = Column(String(50), nullable=False)
    tool_level = Column(Integer, nullable=False, server_default=text("1"))

    max_durability = Column(Integer, nullable=False)
    durability_cost_per_use = Column(Integer, nullable=False, server_default=text("1"))

    crop_growth_reduction_seconds = Column(Integer, nullable=False, server_default=text("0"))
    fishing_cooldown_reduction_seconds = Column(Integer, nullable=False, server_default=text("0"))
    fishing_success_rate = Column(Numeric(3, 2), nullable=False, server_default=text("0.00"))
    fishing_catch_quantity = Column(Integer, nullable=False, server_default=text("1"))
    harvest_bonus_percent = Column(Integer, nullable=False, server_default=text("0"))
    milk_bonus_quantity = Column(Integer, nullable=False, server_default=text("0"))

    is_active = Column(Integer, nullable=False, server_default=text("1"))

    created_at = Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(
        DateTime,
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
        server_onupdate=text("CURRENT_TIMESTAMP"),
    )

    item = relationship("Item")
    user_tools = relationship("UserTool", back_populates="tool_template")
