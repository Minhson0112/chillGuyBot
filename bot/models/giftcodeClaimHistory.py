from sqlalchemy import BigInteger, Column, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from bot.config.database import Base


class GiftcodeClaimHistory(Base):
    __tablename__ = "giftcode_claim_histories"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="giftcode claim history id")

    user_id = Column(
        BigInteger,
        ForeignKey("member.user_id", ondelete="CASCADE"),
        nullable=False,
        comment="discord user id",
    )

    giftcode_id = Column(
        BigInteger,
        ForeignKey("giftcodes.id", ondelete="CASCADE"),
        nullable=False,
        comment="giftcode id",
    )

    created_at = Column(DateTime, nullable=False, server_default=func.now(), comment="created at")

    member = relationship("Member")
    giftcode = relationship("Giftcode")