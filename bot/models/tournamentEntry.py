from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, Integer
from sqlalchemy.orm import relationship

from bot.config.database import Base


class TournamentEntry(Base):
    __tablename__ = "tournament_entry"

    id_tournament = Column(BigInteger, ForeignKey("tournament_master.id_tournament"), primary_key=True, nullable=False)
    user_id = Column(BigInteger, ForeignKey("member.user_id"), primary_key=True, nullable=False)
    registered_at = Column(DateTime, nullable=False)
    status = Column(Integer, nullable=False, default=0, comment="0: signing, 1: entry confirm, 2: eliminated")

    tournamentMaster = relationship("TournamentMaster", back_populates="tournamentEntries")
    member = relationship("Member", back_populates="tournamentEntries")