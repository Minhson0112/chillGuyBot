from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, Index, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from bot.config.database import Base
from bot.enums.giveawayWinnerStatus import GiveawayWinnerStatus


class GiveawayWinner(Base):
    __tablename__ = "giveaway_winners"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="giveaway winner id")

    giveaway_id = Column(
        BigInteger,
        ForeignKey("giveaway.id", ondelete="CASCADE"),
        nullable=False,
        comment="giveaway id",
    )
    user_id = Column(
        BigInteger,
        ForeignKey("member.user_id", ondelete="CASCADE"),
        nullable=False,
        comment="discord user id",
    )

    draw_round = Column(Integer, nullable=False, default=1, comment="draw or reroll round")
    slot_number = Column(Integer, nullable=False, comment="winner slot number")
    current_slot_number = Column(Integer, nullable=True, comment="current active winner slot number, null for rerolled winners")

    status = Column(String(50), nullable=False, default=GiveawayWinnerStatus.SELECTED.value, comment="winner status: selected, claimed, disqualified, rerolled")
    disqualified_reason = Column(String(255), nullable=True, comment="disqualified reason: missing_role, left_server, no_response, manual_reroll, etc")

    rerolled_from_winner_id = Column(
        BigInteger,
        ForeignKey("giveaway_winners.id", ondelete="SET NULL"),
        nullable=True,
        comment="previous winner id if this row is from reroll",
    )

    selected_at = Column(DateTime, nullable=False, server_default=func.now(), comment="selected at")
    claimed_at = Column(DateTime, nullable=True, comment="claimed at")
    disqualified_at = Column(DateTime, nullable=True, comment="disqualified at")
    created_at = Column(DateTime, nullable=False, server_default=func.now(), comment="created at")
    updated_at = Column(
        DateTime,
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
        comment="updated at",
    )

    giveaway = relationship(
        "Giveaway",
        foreign_keys=[giveaway_id],
        back_populates="winners",
    )
    member = relationship("Member", foreign_keys=[user_id])
    rerolledFromWinner = relationship("GiveawayWinner", remote_side=[id])
