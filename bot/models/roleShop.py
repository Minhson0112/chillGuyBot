from sqlalchemy import BigInteger, Boolean, Column, DateTime, Integer, String, UniqueConstraint, func
from sqlalchemy.orm import relationship

from bot.config.database import Base


class RoleShop(Base):
    __tablename__ = "role_shop"

    id = Column(BigInteger, primary_key=True, autoincrement=True)

    role_id = Column(BigInteger, nullable=False)
    
    price_cowoncy = Column(BigInteger, nullable=True)
    price_chill_coin = Column(BigInteger, nullable=True)

    valid_days = Column(Integer, nullable=False, default=30)

    is_active = Column(Boolean, nullable=False, default=True)
    sort_order = Column(Integer, nullable=False, default=0)

    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    member_role_purchases = relationship("MemberRolePurchase", back_populates="role_shop")

    __table_args__ = (
        UniqueConstraint("role_id", name="uq_role_shop_role"),
    )