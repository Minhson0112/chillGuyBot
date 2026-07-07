from datetime import datetime

from bot.config.database import getDbSession
from bot.enums.memberPaymentTargetType import MemberPaymentTargetType
from bot.helper.numberFormatHelper import formatNumber
from bot.helper.serverItemHelper import buildServerItemText, getServerItemEmoji
from bot.repository.memberPaymentTransactionRepository import MemberPaymentTransactionRepository
from bot.repository.serverItemMasterRepository import ServerItemMasterRepository
from bot.repository.serverItemPurchaseRepository import ServerItemPurchaseRepository


class ServerItemPurchaseService:
    def createPendingPurchase(
        self,
        userId: int,
        itemId: int,
        quantity: int,
    ):
        if quantity <= 0:
            return {
                "success": False,
                "message": "Số lượng item phải lớn hơn 0.",
            }

        now = datetime.now()

        with getDbSession() as session:
            serverItemMasterRepository = ServerItemMasterRepository(session)
            serverItemPurchaseRepository = ServerItemPurchaseRepository(session)
            memberPaymentTransactionRepository = MemberPaymentTransactionRepository(session)

            serverItem = serverItemMasterRepository.findActiveById(itemId)

            if serverItem is None:
                return {
                    "success": False,
                    "message": "Item này hiện không được bán trong love shop.",
                }

            requiredCowoncyAmount = self.normalizePrice(serverItem.price_cowoncy)
            requiredChillCoinAmount = self.normalizePrice(serverItem.price_chill_coin)

            if requiredCowoncyAmount is None and requiredChillCoinAmount is None:
                return {
                    "success": False,
                    "message": "Item này chưa có giá thanh toán hợp lệ.",
                }

            pendingPayment = memberPaymentTransactionRepository.findPendingPaymentByUserId(userId)

            if pendingPayment is not None:
                return self.buildPendingPaymentResult(
                    serverItemPurchaseRepository=serverItemPurchaseRepository,
                    pendingPayment=pendingPayment,
                )

            requiredCowoncyAmount = self.multiplyPrice(requiredCowoncyAmount, quantity)
            requiredChillCoinAmount = self.multiplyPrice(requiredChillCoinAmount, quantity)
            serverItemPurchase = serverItemPurchaseRepository.createPendingPurchase(
                userId=userId,
                itemId=serverItem.id,
                quantity=quantity,
                registeredAt=now,
            )

            memberPaymentTransactionRepository.createPendingPayment(
                userId=userId,
                paymentTargetType=MemberPaymentTargetType.LOVE_SHOP.value,
                paymentTargetId=serverItemPurchase.id,
                requiredCowoncyAmount=requiredCowoncyAmount,
                requiredChillCoinAmount=requiredChillCoinAmount,
                registeredAt=now,
            )

            session.commit()

            return {
                "success": True,
                "itemName": serverItem.name,
                "itemEmoji": getServerItemEmoji(serverItem),
                "quantity": quantity,
                "priceCowoncy": requiredCowoncyAmount,
                "priceChillCoin": requiredChillCoinAmount,
            }

    def buildPendingPaymentResult(
        self,
        serverItemPurchaseRepository: ServerItemPurchaseRepository,
        pendingPayment,
    ):
        if pendingPayment.payment_target_type != MemberPaymentTargetType.LOVE_SHOP.value:
            return {
                "success": False,
                "message": "Bạn đang có giao dịch khác đang chờ thanh toán. Hãy thanh toán hoặc hủy giao dịch đó trước.",
            }

        pendingPurchase = serverItemPurchaseRepository.findById(pendingPayment.payment_target_id)

        if pendingPurchase is None or pendingPurchase.item is None:
            return {
                "success": False,
                "message": "Bạn đang có giao dịch love shop đang chờ thanh toán. Hãy thanh toán hoặc dùng `cg cancelloveshop` để hủy giao dịch.",
            }

        return {
            "success": False,
            "message": (
                "Bạn đang có giao dịch love shop đang chờ thanh toán.\n"
                f"Item đang chờ: {buildServerItemText(pendingPurchase.item)} x**{formatNumber(pendingPurchase.quantity)}**.\n"
                "Hãy thanh toán hoặc dùng `cg cancelloveshop` để hủy giao dịch."
            ),
        }

    def normalizePrice(self, price):
        if price is None or price <= 0:
            return None

        return price

    def multiplyPrice(self, price, quantity: int):
        if price is None:
            return None

        return price * quantity
