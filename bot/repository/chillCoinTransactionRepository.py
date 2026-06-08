from datetime import datetime, timedelta

from sqlalchemy import asc, desc, func
from sqlalchemy.orm import joinedload

from bot.enums.chillCoinTransactionType import ChillCoinTransactionType
from bot.models.chillCoinTransaction import ChillCoinTransaction


class ChillCoinTransactionRepository:
    def __init__(self, session):
        self.session = session

    def create(
        self,
        fromUserId: int,
        toUserId: int,
        amount: int,
        transactionType: str = ChillCoinTransactionType.TRANSFER.value,
        note: str = None,
    ):
        transaction = ChillCoinTransaction(
            from_user_id=fromUserId,
            to_user_id=toUserId,
            amount=amount,
            transaction_type=transactionType,
            note=note,
        )

        self.session.add(transaction)
        self.session.flush()

        return transaction

    def sumReceivedAmountByUserIdBetween(
        self,
        userId: int,
        startAt: datetime,
        endAt: datetime,
        transactionType: str = ChillCoinTransactionType.TRANSFER.value,
    ):
        totalAmount = (
            self.session.query(func.coalesce(func.sum(ChillCoinTransaction.amount), 0))
            .filter(ChillCoinTransaction.to_user_id == userId)
            .filter(ChillCoinTransaction.transaction_type == transactionType)
            .filter(ChillCoinTransaction.created_at >= startAt)
            .filter(ChillCoinTransaction.created_at < endAt)
            .scalar()
        )

        return int(totalAmount)

    def findRecentByUserId(
        self,
        userId: int,
        limit: int = 10,
    ):
        return (
            self.session.query(ChillCoinTransaction)
            .options(
                joinedload(ChillCoinTransaction.fromMember),
                joinedload(ChillCoinTransaction.toMember),
            )
            .filter(
                (ChillCoinTransaction.from_user_id == userId)
                | (ChillCoinTransaction.to_user_id == userId)
            )
            .order_by(
                desc(ChillCoinTransaction.created_at),
                desc(ChillCoinTransaction.id),
            )
            .limit(limit)
            .all()
        )
