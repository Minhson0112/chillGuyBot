from sqlalchemy import BigInteger, Boolean, Column, DateTime, ForeignKey, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from bot.config.database import Base


class FarmMarketListing(Base):
    __tablename__ = "farm_market_listings"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="market listing id")

    seller_user_id = Column(
        BigInteger,
        ForeignKey("member.user_id", ondelete="CASCADE"),
        nullable=False,
        comment="seller discord user id",
    )

    buyer_user_id = Column(
        BigInteger,
        ForeignKey("member.user_id", ondelete="SET NULL"),
        nullable=True,
        comment="buyer discord user id",
    )

    item_id = Column(
        BigInteger,
        ForeignKey("items.id", ondelete="RESTRICT"),
        nullable=False,
        comment="listed item id",
    )

    quantity = Column(BigInteger, nullable=False, default=1, comment="listed item quantity")
    price = Column(Integer, nullable=False, comment="total base selling price")
    is_sold = Column(Boolean, nullable=False, default=False, comment="whether item has been sold")

    created_at = Column(DateTime, nullable=False, server_default=func.now(), comment="created at")
    sold_at = Column(DateTime, nullable=True, comment="sold at")

    seller = relationship(
        "Member",
        foreign_keys=[seller_user_id],
        back_populates="marketListings",
    )

    buyer = relationship(
        "Member",
        foreign_keys=[buyer_user_id],
        back_populates="marketPurchases",
    )

    item = relationship("Item", back_populates="marketListings")
