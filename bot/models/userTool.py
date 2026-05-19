from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, Integer, String, text
from sqlalchemy.orm import relationship

from bot.config.database import Base


class UserTool(Base):
    __tablename__ = "user_tools"

    id = Column(BigInteger, primary_key=True, autoincrement=True)

    user_id = Column(
        BigInteger,
        ForeignKey("member.user_id", ondelete="CASCADE"),
        nullable=False,
    )

    item_id = Column(
        BigInteger,
        ForeignKey("items.id", ondelete="RESTRICT"),
        nullable=False,
    )

    tool_template_id = Column(
        BigInteger,
        ForeignKey("tool_templates.id", ondelete="RESTRICT"),
        nullable=False,
    )

    current_durability = Column(Integer, nullable=False)
    status = Column(String(50), nullable=False, server_default=text("'available'"))

    acquired_at = Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    created_at = Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(
        DateTime,
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
        server_onupdate=text("CURRENT_TIMESTAMP"),
    )

    member = relationship("Member")
    item = relationship("Item")
    tool_template = relationship("ToolTemplate", back_populates="user_tools")
    farm_tool_equipment = relationship(
        "FarmToolEquipment",
        back_populates="user_tool",
        uselist=False,
    )