from datetime import datetime, timedelta

from sqlalchemy import asc, desc
from sqlalchemy.orm import joinedload

from bot.models.farmMarketListing import FarmMarketListing


class FarmMarketListingRepository:
    def __init__(self, session):
        self.session = session

    def create(
        self,
        sellerUserId: int,
        itemId: int,
        quantity: int,
        price: int,
    ):
        farmMarketListing = FarmMarketListing(
            seller_user_id=sellerUserId,
            item_id=itemId,
            quantity=quantity,
            price=price,
            is_sold=False,
            buyer_user_id=None,
            sold_at=None,
        )

        self.session.add(farmMarketListing)
        self.session.flush()

        return farmMarketListing

    def findById(self, listingId: int):
        return (
            self.session.query(FarmMarketListing)
            .filter(FarmMarketListing.id == listingId)
            .first()
        )

    def findByIdWithItem(self, listingId: int):
        return (
            self.session.query(FarmMarketListing)
            .options(joinedload(FarmMarketListing.item))
            .filter(FarmMarketListing.id == listingId)
            .first()
        )

    def findOpenListings(self):
        return (
            self.session.query(FarmMarketListing)
            .options(
                joinedload(FarmMarketListing.item),
                joinedload(FarmMarketListing.seller),
            )
            .filter(FarmMarketListing.is_sold.is_(False))
            .order_by(
                asc(FarmMarketListing.created_at),
                asc(FarmMarketListing.id),
            )
            .all()
        )

    def findOpenListingsByPage(self, page: int, perPage: int):
        offset = (page - 1) * perPage

        return (
            self.session.query(FarmMarketListing)
            .options(
                joinedload(FarmMarketListing.item),
                joinedload(FarmMarketListing.seller),
            )
            .filter(FarmMarketListing.is_sold.is_(False))
            .order_by(
                asc(FarmMarketListing.created_at),
                asc(FarmMarketListing.id),
            )
            .offset(offset)
            .limit(perPage)
            .all()
        )

    def countOpenListings(self):
        return (
            self.session.query(FarmMarketListing)
            .filter(FarmMarketListing.is_sold.is_(False))
            .count()
        )

    def markSold(
        self,
        farmMarketListing: FarmMarketListing,
        buyerUserId: int,
    ):
        farmMarketListing.is_sold = True
        farmMarketListing.buyer_user_id = buyerUserId
        farmMarketListing.sold_at = datetime.now()

        self.session.flush()

        return farmMarketListing
    
    def findExpiredOpenListings(self, now: datetime, expiredHours: int):
        expiredAt = now - timedelta(hours=expiredHours)

        return (
            self.session.query(FarmMarketListing)
            .options(
                joinedload(FarmMarketListing.item),
                joinedload(FarmMarketListing.seller),
            )
            .filter(FarmMarketListing.is_sold.is_(False))
            .filter(FarmMarketListing.created_at <= expiredAt)
            .order_by(
                asc(FarmMarketListing.created_at),
                asc(FarmMarketListing.id),
            )
            .all()
        )
    
    def countOpenListingsBySellerUserId(self, sellerUserId: int):
        return (
            self.session.query(FarmMarketListing)
            .filter(FarmMarketListing.seller_user_id == sellerUserId)
            .filter(FarmMarketListing.is_sold.is_(False))
            .count()
        )

    def findOpenListingsBySellerUserIdAndPage(
        self,
        sellerUserId: int,
        page: int,
        perPage: int,
    ):
        offset = (page - 1) * perPage

        return (
            self.session.query(FarmMarketListing)
            .options(
                joinedload(FarmMarketListing.item),
                joinedload(FarmMarketListing.seller),
            )
            .filter(FarmMarketListing.seller_user_id == sellerUserId)
            .filter(FarmMarketListing.is_sold.is_(False))
            .order_by(
                asc(FarmMarketListing.created_at),
                asc(FarmMarketListing.id),
            )
            .offset(offset)
            .limit(perPage)
            .all()
        )
    
    def findByIdWithItemAndSeller(self, listingId: int):
        return (
            self.session.query(FarmMarketListing)
            .options(
                joinedload(FarmMarketListing.item),
                joinedload(FarmMarketListing.seller),
            )
            .filter(FarmMarketListing.id == listingId)
            .first()
        )
    
    def findFirstOpenListingByItemId(self, itemId: int):
        return (
            self.session.query(FarmMarketListing)
            .options(
                joinedload(FarmMarketListing.item),
                joinedload(FarmMarketListing.seller),
            )
            .filter(FarmMarketListing.item_id == itemId)
            .filter(FarmMarketListing.is_sold.is_(False))
            .order_by(
                asc(FarmMarketListing.created_at),
                asc(FarmMarketListing.id),
            )
            .first()
        )
    
    def findSoldListingsBySellerUserId(
        self,
        sellerUserId: int,
        limit: int = 10,
    ):
        return (
            self.session.query(FarmMarketListing)
            .options(
                joinedload(FarmMarketListing.item),
                joinedload(FarmMarketListing.buyer),
            )
            .filter(FarmMarketListing.seller_user_id == sellerUserId)
            .filter(FarmMarketListing.is_sold.is_(True))
            .order_by(
                desc(FarmMarketListing.sold_at),
                desc(FarmMarketListing.id),
            )
            .limit(limit)
            .all()
        )