from sqlalchemy import BigInteger, Boolean, Column, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from bot.config.database import Base


class MemberBaseSkinInventory(Base):
    __tablename__ = "member_base_skin_inventory"
    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "base_skin_id",
            name="uq_member_base_skin_inventory_user_skin",
        ),
    )

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="member base skin inventory id")
    user_id = Column(
        BigInteger,
        ForeignKey("member.user_id", ondelete="CASCADE"),
        nullable=False,
        comment="discord user id",
    )
    base_skin_id = Column(
        BigInteger,
        ForeignKey("base_skin_master.id", ondelete="RESTRICT"),
        nullable=False,
        comment="base skin id",
    )
    is_using = Column(Boolean, nullable=False, default=False, comment="is currently in use")
    acquired_at = Column(DateTime, nullable=False, server_default=func.now(), comment="acquired at")
    created_at = Column(DateTime, nullable=False, server_default=func.now(), comment="created at")
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now(), comment="updated at")

    member = relationship("Member", back_populates="baseSkinInventories")
    baseSkin = relationship("BaseSkinMaster", back_populates="memberInventories")
