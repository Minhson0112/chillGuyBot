import random
from datetime import datetime, timedelta, timezone

from google import genai
from google.genai import types

from bot.config.channel import BIRTHDAY_CHANNEL_ID
from bot.config.config import GEMINI_API_KEY, GEMINI_MODEL
from bot.config.database import getDbSession
from bot.repository.memberDailyFortuneRepository import MemberDailyFortuneRepository
from bot.repository.memberRepository import MemberRepository


class DailyFortuneService:
    GMT7 = timezone(timedelta(hours=7))

    def getDailyFortune(self, userId: int):
        today = self.getTodayDate()

        with getDbSession() as session:
            memberRepository = MemberRepository(session)
            memberDailyFortuneRepository = MemberDailyFortuneRepository(session)

            member = memberRepository.findByUserId(userId)

            if member is None:
                return {
                    "success": False,
                    "message": "Không tìm thấy dữ liệu member của bạn.",
                }

            if member.date_of_birth is None:
                return {
                    "success": False,
                    "message": (
                        f"Hãy cho tớ biết ngày sinh của bạn bằng lệnh `cg sn` "
                        f"ở <#{BIRTHDAY_CHANNEL_ID}> trước nhé."
                    ),
                }

            dailyFortune = memberDailyFortuneRepository.findByUserIdAndFortuneDate(
                userId=userId,
                fortuneDate=today,
            )

            if dailyFortune is not None:
                return {
                    "success": True,
                    "dailyFortune": dailyFortune,
                    "fortuneDate": today,
                }

            if not GEMINI_API_KEY:
                return {
                    "success": False,
                    "message": "Có lỗi, xin vui lòng thử lại sau.",
                }

            loveRate = random.randint(0, 100)
            luckRate = random.randint(0, 100)
            careerRate = random.randint(0, 100)
            description = self.generateFortuneDescription(
                dateOfBirth=member.date_of_birth,
                loveRate=loveRate,
                luckRate=luckRate,
                careerRate=careerRate,
            )

            dailyFortune = memberDailyFortuneRepository.create(
                userId=userId,
                fortuneDate=today,
                loveRate=loveRate,
                luckRate=luckRate,
                careerRate=careerRate,
                description=description,
            )

            session.commit()

            return {
                "success": True,
                "dailyFortune": dailyFortune,
                "fortuneDate": today,
            }

    def getTodayDate(self):
        return datetime.now(self.GMT7).date()

    def generateFortuneDescription(
        self,
        dateOfBirth,
        loveRate: int,
        luckRate: int,
        careerRate: int,
    ):
        client = genai.Client(api_key=GEMINI_API_KEY)
        prompt = self.buildFortunePrompt(
            dateOfBirth=dateOfBirth,
            loveRate=loveRate,
            luckRate=luckRate,
            careerRate=careerRate,
        )

        description = ""

        for _ in range(2):
            response = client.models.generate_content(
                model=GEMINI_MODEL,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=1.1,
                    max_output_tokens=10000,
                ),
            )

            description = response.text.strip() if response.text is not None else ""

            if description != "" and not self.hasForbiddenFortuneText(description):
                break

        if description == "":
            raise ValueError("Gemini response is empty")

        if self.hasForbiddenFortuneText(description):
            raise ValueError("Gemini response contains forbidden fortune text")

        return description

    def hasForbiddenFortuneText(self, description: str):
        lowerDescription = description.lower()
        forbiddenTexts = [
            "chào mừng tuổi mới",
            "bạn sinh",
            "sinh ngày",
            "ngày sinh",
            "tuổi mới",
            "cung ",
        ]

        return any(text in lowerDescription for text in forbiddenTexts)

    def buildFortunePrompt(
        self,
        dateOfBirth,
        loveRate: int,
        luckRate: int,
        careerRate: int,
    ):
        return (
            "Bạn là một thầy bói vui tính.\n"
            "Dựa trên các chỉ số sau:\n"
            f"- Ngày Sinh: {dateOfBirth.strftime('%d-%m-%Y')}\n"
            f"- Điểm tình yêu: {loveRate}/100\n"
            f"- Điểm may mắn: {luckRate}/100\n"
            f"- Điểm công việc, học tập: {careerRate}/100\n\n"
            "Hãy viết một đoạn bói toán hài hước bằng tiếng Việt khoảng 100 từ dựa trên chỉ số bên trên.\n"
            "Không nhắc đến ngày sinh, tuổi mới, hoặc bất kỳ con số nào từ Ngày Sinh.\n"
            "Chỉ trả về nội dung bói toán, không tiêu đề, không markdown, không bullet."
        )
