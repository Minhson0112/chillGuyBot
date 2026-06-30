from sqlalchemy import BigInteger, Boolean, Column, Date, Integer, DateTime, String
from sqlalchemy.orm import relationship

from bot.config.database import Base


class Member(Base):
    __tablename__ = "member"

    user_id = Column(BigInteger, primary_key=True, comment="id discord")
    global_name = Column(String(255), nullable=True, comment="global name in discord")
    username = Column(String(255), nullable=False, comment="username in discord")
    nick = Column(String(255), nullable=True, comment="username in chill station")
    date_of_birth = Column(Date, nullable=True, comment="date of birth")
    joined_at = Column(DateTime, nullable=False, comment="join chill station at")
    leave_at = Column(DateTime, nullable=True, comment="leave chill station at")
    is_bot = Column(Boolean, nullable=False, comment="is bot?")
    join_count = Column(Integer, nullable=False, default=1, comment="number of times the member has joined the server")
    warning_count = Column(Integer, nullable=False, default=0, comment="number of warnings for rule violations")
    is_partner = Column(Boolean, nullable=False, default=False, comment="is partner member?")
    correct_word_guess_count = Column(Integer, nullable=False, default=0, comment="number of times the member guessed the correct word")
    chill_coin = Column(Integer, nullable=False, default=0, comment="server private currency")
    is_staff = Column(Boolean, nullable=False, default=False, comment="is staff member")
    is_mod = Column(Boolean, nullable=False, default=False, comment="is moderator member")
    is_admin = Column(Boolean, nullable=False, default=False, comment="is admin member")
    can_create_auto_res = Column(Boolean, nullable=False, default=False, comment="can create auto responder")
    is_allow_notifications = Column(Boolean, nullable=False, default=False, comment="is allowed to receive notifications")


    chat = relationship("Chat", back_populates="member", uselist=False)
    tournamentEntries = relationship("TournamentEntry", back_populates="member")
    moderationActions = relationship("MemberModerationHistory", foreign_keys="MemberModerationHistory.action_by_user_id", back_populates="actionByMember")
    moderationTargets = relationship("MemberModerationHistory", foreign_keys="MemberModerationHistory.target_user_id", back_populates="targetMember")
    musicEventEntries = relationship("MusicEventEntry", back_populates="member", cascade="all, delete-orphan")
    farm = relationship("Farm", back_populates="member", uselist=False, cascade="all, delete-orphan")
    inventories = relationship("UserInventory", back_populates="member", cascade="all, delete-orphan")
    baseSkinInventories = relationship(
        "MemberBaseSkinInventory",
        back_populates="member",
        cascade="all, delete-orphan",
    )
    fishingHistories = relationship("FishingHistory", back_populates="member", cascade="all, delete-orphan")
    cookingHistories = relationship("FarmCookingHistory", back_populates="member", cascade="all, delete-orphan")
    harvestHistories = relationship("FarmHarvestHistory", back_populates="member", cascade="all, delete-orphan")
    mergeGamePlayHistories = relationship("MergeGamePlayHistory", back_populates="member", cascade="all, delete-orphan")
    marketListings = relationship(
        "FarmMarketListing",
        foreign_keys="FarmMarketListing.seller_user_id",
        back_populates="seller",
        cascade="all, delete-orphan",
    )
    marketPurchases = relationship(
        "FarmMarketListing",
        foreign_keys="FarmMarketListing.buyer_user_id",
        back_populates="buyer",
    )
    dailyActivities = relationship(
        "MemberDailyActivity",
        back_populates="member",
        cascade="all, delete-orphan",
    )
    dailyFortunes = relationship(
        "MemberDailyFortune",
        back_populates="member",
        cascade="all, delete-orphan",
    )
    dailyCheckinHistories = relationship(
        "DailyCheckinHistory",
        back_populates="member",
        cascade="all, delete-orphan",
    )
