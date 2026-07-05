from sqlalchemy import CheckConstraint, Column, DateTime, ForeignKey, Index, String
from sqlalchemy.dialects.mysql import BIGINT
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from bot.config.database import Base


class ServerItemPurchase(Base):
    __tablename__ = "server_item_purchase"
    __table_args__ = (
        Index("idx_server_item_purchase_user_status", "user_id", "status"),
        Index("idx_server_item_purchase_item_status", "item_id", "status"),
        Index(
            "idx_server_item_purchase_status_registered_at",
            "status",
            "registered_at",
        ),
        CheckConstraint(
            "quantity > 0",
            name="chk_server_item_purchase_quantity",
        ),
        CheckConstraint(
            "status IN ('pending_payment', 'paid', 'cancelled', 'expired')",
            name="chk_server_item_purchase_status",
        ),
        CheckConstraint(
            "payment_type IS NULL OR payment_type IN ('cowoncy', 'chill_coin')",
            name="chk_server_item_purchase_payment_type",
        ),
        CheckConstraint(
            "payment_amount IS NULL OR payment_amount > 0",
            name="chk_server_item_purchase_payment_amount",
        ),
    )

    id = Column(BIGINT, primary_key=True, autoincrement=True, comment="server item purchase id")
    user_id = Column(
        BIGINT(unsigned=True),
        ForeignKey("member.user_id", ondelete="CASCADE"),
        nullable=False,
        comment="discord user id",
    )
    item_id = Column(
        BIGINT,
        ForeignKey("server_item_master.id", ondelete="RESTRICT"),
        nullable=False,
        comment="server item id",
    )
    quantity = Column(
        BIGINT(unsigned=True),
        nullable=False,
        comment="item quantity",
    )
    status = Column(
        String(50),
        nullable=False,
        comment="purchase status: pending_payment, paid, cancelled, expired",
    )
    payment_type = Column(
        String(50),
        nullable=True,
        comment="actual payment type: cowoncy, chill_coin",
    )
    payment_amount = Column(
        BIGINT(unsigned=True),
        nullable=True,
        comment="actual payment amount",
    )
    registered_at = Column(
        DateTime,
        nullable=False,
        server_default=func.now(),
        comment="registered at",
    )
    paid_at = Column(DateTime, nullable=True, comment="paid at")
    expired_at = Column(DateTime, nullable=True, comment="expired at")
    created_at = Column(DateTime, nullable=False, server_default=func.now(), comment="created at")
    updated_at = Column(
        DateTime,
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
        comment="updated at",
    )

    member = relationship("Member")
    item = relationship("ServerItemMaster", back_populates="purchases")
