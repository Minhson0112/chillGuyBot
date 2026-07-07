from datetime import datetime

from bot.config.database import getDbSession
from bot.enums.memberPaymentStatus import MemberPaymentStatus
from bot.enums.memberPaymentTargetType import MemberPaymentTargetType
from bot.enums.paymentType import PaymentType
from bot.enums.serverItemPurchaseStatus import ServerItemPurchaseStatus
from bot.helper.serverItemHelper import getServerItemEmoji
from bot.repository.memberPaymentTransactionRepository import MemberPaymentTransactionRepository
from bot.repository.serverItemPurchaseRepository import ServerItemPurchaseRepository
from bot.repository.serverUserInventoryRepository import ServerUserInventoryRepository


class ServerItemPaymentService:
    def verifyPayment(self, memberPaymentTransactionId: int, paymentType: str, paymentAmount: int):
        if paymentAmount <= 0:
            return {
                "success": False,
                "message": "Số tiền thanh toán không hợp lệ.",
            }

        with getDbSession() as session:
            memberPaymentTransactionRepository = MemberPaymentTransactionRepository(session)
            serverItemPurchaseRepository = ServerItemPurchaseRepository(session)
            pendingPayment = memberPaymentTransactionRepository.findById(memberPaymentTransactionId)

            if pendingPayment is None:
                return {
                    "success": False,
                    "message": "Không tìm thấy giao dịch thanh toán.",
                }

            if pendingPayment.status != MemberPaymentStatus.PENDING_PAYMENT.value:
                return {
                    "success": False,
                    "message": "Giao dịch thanh toán này không còn ở trạng thái chờ thanh toán.",
                }

            if pendingPayment.payment_target_type != MemberPaymentTargetType.LOVE_SHOP.value:
                return {
                    "success": False,
                    "message": "Giao dịch thanh toán này không phải giao dịch love shop.",
                }

            pendingPurchase = serverItemPurchaseRepository.findById(pendingPayment.payment_target_id)

            if pendingPurchase is None:
                return {
                    "success": False,
                    "message": "Không tìm thấy giao dịch mua item love shop.",
                }

            if pendingPurchase.status != ServerItemPurchaseStatus.PENDING_PAYMENT.value:
                return {
                    "success": False,
                    "message": "Giao dịch mua item này không còn ở trạng thái chờ thanh toán.",
                }

            serverItem = pendingPurchase.item

            if serverItem is None:
                return {
                    "success": False,
                    "message": "Không tìm thấy thông tin item của giao dịch này.",
                }

            requiredAmount = self.getRequiredAmount(
                pendingPayment=pendingPayment,
                paymentType=paymentType,
            )

            if requiredAmount is None or requiredAmount <= 0:
                return {
                    "success": False,
                    "message": "Item này không hỗ trợ phương thức thanh toán này.",
                    "itemName": serverItem.name,
                    "itemEmoji": getServerItemEmoji(serverItem),
                    "quantity": pendingPurchase.quantity,
                }

            if paymentAmount < requiredAmount:
                return {
                    "success": False,
                    "message": f"Số tiền thanh toán chưa đủ. Bạn cần thanh toán **{requiredAmount:,}**, hiện tại mới nhận được **{paymentAmount:,}**.",
                    "itemName": serverItem.name,
                    "itemEmoji": getServerItemEmoji(serverItem),
                    "quantity": pendingPurchase.quantity,
                    "requiredAmount": requiredAmount,
                    "paymentAmount": paymentAmount,
                }

            return {
                "success": True,
                "memberPaymentTransactionId": pendingPayment.id,
                "serverItemPurchaseId": pendingPurchase.id,
                "itemId": serverItem.id,
                "itemName": serverItem.name,
                "itemEmoji": getServerItemEmoji(serverItem),
                "quantity": pendingPurchase.quantity,
                "requiredAmount": requiredAmount,
                "paymentAmount": paymentAmount,
                "paymentType": paymentType,
            }

    def completePayment(self, memberPaymentTransactionId: int, paymentType: str, paymentAmount: int):
        now = datetime.now()

        with getDbSession() as session:
            memberPaymentTransactionRepository = MemberPaymentTransactionRepository(session)
            serverItemPurchaseRepository = ServerItemPurchaseRepository(session)
            serverUserInventoryRepository = ServerUserInventoryRepository(session)
            memberPaymentTransaction = memberPaymentTransactionRepository.findById(memberPaymentTransactionId)

            if memberPaymentTransaction is None:
                return {
                    "success": False,
                    "message": "Không tìm thấy giao dịch thanh toán.",
                }

            if memberPaymentTransaction.status != MemberPaymentStatus.PENDING_PAYMENT.value:
                return {
                    "success": False,
                    "message": "Giao dịch thanh toán này không còn ở trạng thái chờ thanh toán.",
                }

            if memberPaymentTransaction.payment_target_type != MemberPaymentTargetType.LOVE_SHOP.value:
                return {
                    "success": False,
                    "message": "Giao dịch thanh toán này không phải giao dịch love shop.",
                }

            serverItemPurchase = serverItemPurchaseRepository.findById(memberPaymentTransaction.payment_target_id)

            if serverItemPurchase is None:
                return {
                    "success": False,
                    "message": "Không tìm thấy giao dịch mua item love shop.",
                }

            if serverItemPurchase.status != ServerItemPurchaseStatus.PENDING_PAYMENT.value:
                return {
                    "success": False,
                    "message": "Giao dịch này không còn ở trạng thái chờ thanh toán.",
                }

            serverItem = serverItemPurchase.item

            if serverItem is None:
                return {
                    "success": False,
                    "message": "Không tìm thấy thông tin item của giao dịch này.",
                }

            serverUserInventoryRepository.upsertQuantity(
                userId=serverItemPurchase.user_id,
                itemId=serverItemPurchase.item_id,
                quantity=serverItemPurchase.quantity,
            )

            serverItemPurchase.status = ServerItemPurchaseStatus.PAID.value
            serverItemPurchase.payment_type = paymentType
            serverItemPurchase.payment_amount = paymentAmount
            serverItemPurchase.paid_at = now

            memberPaymentTransaction.status = MemberPaymentStatus.PAID.value
            memberPaymentTransaction.paid_payment_type = paymentType
            memberPaymentTransaction.paid_amount = paymentAmount
            memberPaymentTransaction.paid_at = now

            session.commit()

            return {
                "success": True,
                "itemName": serverItem.name,
                "itemEmoji": getServerItemEmoji(serverItem),
                "quantity": serverItemPurchase.quantity,
            }

    def getRequiredAmount(self, pendingPayment, paymentType: str):
        if paymentType == PaymentType.COWONCY.value:
            return pendingPayment.required_cowoncy_amount

        if paymentType == PaymentType.CHILL_COIN.value:
            return pendingPayment.required_chill_coin_amount

        return None
