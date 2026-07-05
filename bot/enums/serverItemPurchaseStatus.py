from enum import Enum


class ServerItemPurchaseStatus(Enum):
    PENDING_PAYMENT = "pending_payment"
    PAID = "paid"
    EXPIRED = "expired"
    CANCELLED = "cancelled"
