from bot.enums.memberPaymentStatus import MemberPaymentStatus
from bot.models.memberPaymentTransaction import MemberPaymentTransaction


class MemberPaymentTransactionRepository:
    def __init__(self, session):
        self.session = session

    def createPendingPayment(
        self,
        userId: int,
        paymentTargetType: str,
        paymentTargetId: int,
        requiredCowoncyAmount: int | None,
        requiredChillCoinAmount: int | None,
        registeredAt,
    ):
        memberPaymentTransaction = MemberPaymentTransaction(
            user_id=userId,
            payment_target_type=paymentTargetType,
            payment_target_id=paymentTargetId,
            status=MemberPaymentStatus.PENDING_PAYMENT.value,
            required_cowoncy_amount=requiredCowoncyAmount,
            required_chill_coin_amount=requiredChillCoinAmount,
            registered_at=registeredAt,
        )

        self.session.add(memberPaymentTransaction)
        self.session.flush()

        return memberPaymentTransaction

    def findById(self, memberPaymentTransactionId: int):
        return (
            self.session.query(MemberPaymentTransaction)
            .filter(MemberPaymentTransaction.id == memberPaymentTransactionId)
            .first()
        )

    def findPendingPaymentByUserId(self, userId: int):
        return (
            self.session.query(MemberPaymentTransaction)
            .filter(
                MemberPaymentTransaction.user_id == userId,
                MemberPaymentTransaction.status == MemberPaymentStatus.PENDING_PAYMENT.value,
            )
            .first()
        )

    def findPendingPaymentByTarget(
        self,
        paymentTargetType: str,
        paymentTargetId: int,
    ):
        return (
            self.session.query(MemberPaymentTransaction)
            .filter(
                MemberPaymentTransaction.payment_target_type == paymentTargetType,
                MemberPaymentTransaction.payment_target_id == paymentTargetId,
                MemberPaymentTransaction.status == MemberPaymentStatus.PENDING_PAYMENT.value,
            )
            .first()
        )
