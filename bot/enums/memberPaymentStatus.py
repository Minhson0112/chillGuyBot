from enum import Enum


class MemberPaymentStatus(Enum):
    PENDING_PAYMENT = "pending_payment"
    PAID = "paid"
    EXPIRED = "expired"
    CANCELLED = "cancelled"
