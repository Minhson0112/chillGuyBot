from datetime import datetime

from bot.config.database import getDbSession
from bot.repository.memberRepository import MemberRepository

MIN_BIRTH_YEAR = 1980
MAX_BIRTH_YEAR = 2020
class MemberBirthdayService:
    def setBirthday(self, userId: int, birthdayText: str):
        try:
            birthday = datetime.strptime(birthdayText, "%d-%m-%Y").date()
        except ValueError:
            return {
                "success": False,
                "message": "Ngày sinh không đúng định dạng. Hãy nhập theo dạng `dd-mm-yyyy`, ví dụ: `cg sn 13-08-2000`.",
            }

        if birthday.year < MIN_BIRTH_YEAR or birthday.year > MAX_BIRTH_YEAR:
            return {
                "success": False,
                "message": "Năm sinh chỉ được phép trong khoảng từ **1980** đến **2020**.",
            }

        with getDbSession() as session:
            memberRepository = MemberRepository(session)
            result = memberRepository.setDateOfBirthIfEmpty(userId, birthday)

            if result is None:
                return {
                    "success": False,
                    "message": "Bạn chưa có dữ liệu trong hệ thống, hãy báo quản trị viên để được hỗ trợ.",
                }

            if result is False:
                return {
                    "success": False,
                    "message": "Bạn đã đăng ký ngày sinh rồi, nếu muốn thay đổi hãy báo quản trị viên để được hỗ trợ.",
                }

            session.commit()

        return {
            "success": True,
            "message": f"Đã lưu ngày sinh của bạn: **{birthday.strftime('%d-%m-%Y')}**🎂",
        }