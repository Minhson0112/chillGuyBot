from datetime import datetime, timedelta

from bot.config.database import getDbSession
from bot.enums.memberPaymentStatus import MemberPaymentStatus
from bot.enums.paymentType import PaymentType
from bot.enums.rolePurchaseStatus import RolePurchaseStatus
from bot.repository.memberPaymentTransactionRepository import MemberPaymentTransactionRepository
from bot.repository.memberRolePurchaseRepository import MemberRolePurchaseRepository


class RoleShopPaymentService:
    def verifyPayment(self, memberPaymentTransactionId: int, paymentType: str, paymentAmount: int):
        if paymentAmount <= 0:
            return {
                "success": False,
                "message": "Số tiền thanh toán không hợp lệ.",
            }

        with getDbSession() as session:
            memberPaymentTransactionRepository = MemberPaymentTransactionRepository(session)
            memberRolePurchaseRepository = MemberRolePurchaseRepository(session)
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

            pendingPurchase = memberRolePurchaseRepository.findById(pendingPayment.payment_target_id)

            if pendingPurchase is None:
                return {
                    "success": False,
                    "message": "Không tìm thấy giao dịch mua role.",
                }

            if pendingPurchase.status != RolePurchaseStatus.PENDING_PAYMENT.value:
                return {
                    "success": False,
                    "message": "Giao dịch mua role này không còn ở trạng thái chờ thanh toán.",
                }

            roleShop = pendingPurchase.role_shop

            if roleShop is None:
                return {
                    "success": False,
                    "message": "Không tìm thấy thông tin role shop của giao dịch này.",
                }

            requiredAmount = self.getRequiredAmount(
                pendingPayment=pendingPayment,
                paymentType=paymentType,
            )

            if requiredAmount is None or requiredAmount <= 0:
                return {
                    "success": False,
                    "message": "Role này không hỗ trợ phương thức thanh toán này.",
                    "roleId": roleShop.role_id,
                }

            if paymentAmount < requiredAmount:
                return {
                    "success": False,
                    "message": f"Số tiền thanh toán chưa đủ. Bạn cần thanh toán **{requiredAmount:,}**, hiện tại mới nhận được **{paymentAmount:,}**.",
                    "roleId": roleShop.role_id,
                    "requiredAmount": requiredAmount,
                    "paymentAmount": paymentAmount,
                }

            return {
                "success": True,
                "memberPaymentTransactionId": pendingPayment.id,
                "memberRolePurchaseId": pendingPurchase.id,
                "roleId": roleShop.role_id,
                "validDays": roleShop.valid_days,
                "requiredAmount": requiredAmount,
                "paymentAmount": paymentAmount,
                "paymentType": paymentType,
            }

    def completePayment(self, memberPaymentTransactionId: int, paymentType: str, paymentAmount: int):
        now = datetime.now()

        with getDbSession() as session:
            memberPaymentTransactionRepository = MemberPaymentTransactionRepository(session)
            memberRolePurchaseRepository = MemberRolePurchaseRepository(session)
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

            memberRolePurchase = memberRolePurchaseRepository.findById(memberPaymentTransaction.payment_target_id)

            if memberRolePurchase is None:
                return {
                    "success": False,
                    "message": "Không tìm thấy giao dịch mua role.",
                }

            if memberRolePurchase.status != RolePurchaseStatus.PENDING_PAYMENT.value:
                return {
                    "success": False,
                    "message": "Giao dịch này không còn ở trạng thái chờ thanh toán.",
                }

            roleShop = memberRolePurchase.role_shop

            if roleShop is None:
                return {
                    "success": False,
                    "message": "Không tìm thấy thông tin role shop của giao dịch này.",
                }

            memberRolePurchase.status = RolePurchaseStatus.PAID.value
            memberRolePurchase.payment_type = paymentType
            memberRolePurchase.payment_amount = paymentAmount
            memberRolePurchase.paid_at = now
            memberRolePurchase.expired_at = now + timedelta(days=roleShop.valid_days)

            memberPaymentTransaction.status = MemberPaymentStatus.PAID.value
            memberPaymentTransaction.paid_payment_type = paymentType
            memberPaymentTransaction.paid_amount = paymentAmount
            memberPaymentTransaction.paid_at = now

            session.commit()

            return {
                "success": True,
                "roleId": roleShop.role_id,
                "expiredAt": memberRolePurchase.expired_at,
            }

    def getRequiredAmount(self, pendingPayment, paymentType: str):
        if paymentType == PaymentType.COWONCY.value:
            return pendingPayment.required_cowoncy_amount

        if paymentType == PaymentType.CHILL_COIN.value:
            return pendingPayment.required_chill_coin_amount

        return None
