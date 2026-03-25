from sqlalchemy import BigInteger, Column, Date, ForeignKey, String

from bot.config.database import Base


class Partner(Base):
    __tablename__ = "partner"

    id = Column(BigInteger, primary_key=True, autoincrement=True, nullable=False)
    guild_id = Column(BigInteger, unique=True, nullable=False)
    guild_name = Column("guild_name", String(255), nullable=False)
    representative_user_id = Column(
        BigInteger,
        ForeignKey("member.user_id"),
        nullable=False
    )
    partnered_by_user_id = Column(
        BigInteger,
        ForeignKey("member.user_id"),
        nullable=False
    )
    partner_at = Column(Date, nullable=False)