from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, String, UniqueConstraint, func
from sqlalchemy.dialects.mysql import BIGINT
from sqlalchemy.orm import relationship

from bot.config.database import Base


class MemberRolePurchase(Base):
    __tablename__ = "member_role_purchase"

    id = Column(BigInteger, primary_key=True, autoincrement=True)

    user_id = Column(BIGINT(unsigned=True), ForeignKey("member.user_id"), nullable=False)
    role_shop_id = Column(BigInteger, ForeignKey("role_shop.id"), nullable=False)

    status = Column(String(50), nullable=False)

    payment_type = Column(String(50), nullable=True)
    payment_amount = Column(BigInteger, nullable=True)

    registered_at = Column(DateTime, nullable=False, server_default=func.now())
    paid_at = Column(DateTime, nullable=True)
    expired_at = Column(DateTime, nullable=True)

    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    member = relationship("Member")
    role_shop = relationship("RoleShop", back_populates="member_role_purchases")

    __table_args__ = (
        UniqueConstraint("user_id", "role_shop_id", name="uq_member_role_purchase_user_role"),
    )