from sqlalchemy import BigInteger, Column, Date

from bot.config.database import Base


class Partner(Base):
    __tablename__ = "partner"

    guild_id = Column(BigInteger, primary_key=True, nullable=False)
    partner_at = Column(Date, nullable=False)