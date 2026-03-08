from sqlalchemy import BigInteger, Column, String, Boolean
from sqlalchemy.orm import relationship

from bot.config.database import Base


class TournamentMaster(Base):
    __tablename__ = "tournament_master"

    id_tournament = Column(BigInteger, primary_key=True, autoincrement=True)
    tournament_name = Column(String(255), nullable=False)
    game_name = Column(String(255), nullable=False)
    total_prize = Column(BigInteger, nullable=False)
    is_available = Column(Boolean, nullable=False, comment="is available tournament?")


    tournamentEntries = relationship("TournamentEntry", back_populates="tournamentMaster")