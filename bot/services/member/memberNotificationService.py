from bot.config.database import getDbSession
from bot.repository.memberRepository import MemberRepository


class MemberNotificationService:
    def updateFarmNotificationSetting(
        self,
        userId: int,
        mode: str,
    ):
        if mode is None:
            return {
                "success": False,
                "message": "Cách dùng: `cg noti on` hoặc `cg noti off`.",
            }

        normalizedMode = mode.lower()

        if normalizedMode not in ["on", "off"]:
            return {
                "success": False,
                "message": "Giá trị không hợp lệ. Hãy dùng `cg noti on` hoặc `cg noti off`.",
            }

        isAllowNotifications = normalizedMode == "on"

        with getDbSession() as session:
            memberRepository = MemberRepository(session)

            member = memberRepository.updateAllowNotifications(
                userId=userId,
                isAllowNotifications=isAllowNotifications,
            )

            if member is None:
                return {
                    "success": False,
                    "message": "Không tìm thấy dữ liệu member của bạn.",
                }

            session.commit()

        if isAllowNotifications:
            return {
                "success": True,
                "message": "Đã bật thông báo farm game cho bạn.",
            }

        return {
            "success": True,
            "message": "Đã tắt thông báo farm game cho bạn.",
        }
