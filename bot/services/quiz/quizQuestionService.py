import asyncio
import html
import inspect
import random
import uuid

import discord
import requests
from googletrans import Translator

from bot.config.channel import QUESTION_CHANNEL_ID
from bot.config.database import getDbSession
from bot.repository.quizAnswerHistoryRepository import QuizAnswerHistoryRepository


class QuizQuestionService:
    QUESTION_API_URL = "https://opentdb.com/api.php?amount=1"

    def __init__(self):
        self.translator = Translator()
        self.currentQuestion = None
        self.questionLock = asyncio.Lock()
        self.hasStarted = False

    async def startOnReady(self, bot):
        if self.hasStarted:
            return

        self.hasStarted = True
        await self.sendNextQuestion(bot)

    async def sendNextQuestion(self, bot):
        channel = bot.get_channel(QUESTION_CHANNEL_ID)
        if channel is None:
            channel = await bot.fetch_channel(QUESTION_CHANNEL_ID)

        questionData = await self.fetchQuestionData()
        if questionData is None:
            await channel.send("Không thể lấy câu hỏi mới từ Open Trivia DB.")
            return None

        async with self.questionLock:
            self.currentQuestion = questionData

        embed = self.buildQuestionEmbed(questionData)

        from bot.views.quiz.quizQuestionAnswerView import QuizQuestionAnswerView

        await channel.send(
            embed=embed,
            view=QuizQuestionAnswerView(questionData["id"], questionData["answers"]),
        )

        return questionData

    async def fetchQuestionData(self):
        try:
            response = await asyncio.to_thread(
                requests.get,
                self.QUESTION_API_URL,
                timeout=10,
            )
            response.raise_for_status()
            data = response.json()
        except Exception as e:
            print(f"Quiz question fetch failed: {e}")
            return None

        if data.get("response_code") != 0:
            print(f"Quiz question API returned response_code={data.get('response_code')}")
            return None

        results = data.get("results", [])
        if not results:
            return None

        question = results[0]
        questionType = question.get("type")
        difficulty = question.get("difficulty")
        categoryEn = html.unescape(question.get("category") or "")
        questionEn = html.unescape(question.get("question") or "")
        correctAnswerEn = html.unescape(question.get("correct_answer") or "")
        incorrectAnswersEn = [
            html.unescape(answer)
            for answer in question.get("incorrect_answers", [])
        ]

        if questionType not in ("boolean", "multiple"):
            return None

        if difficulty not in ("easy", "medium", "hard"):
            return None

        questionVi = await self.translateToVietnamese(questionEn)
        correctAnswerVi = await self.translateAnswerToVietnamese(correctAnswerEn)

        answers = [
            {
                "key": "correct",
                "answerEn": correctAnswerEn,
                "answerVi": correctAnswerVi,
                "isCorrect": True,
            }
        ]

        for index, incorrectAnswerEn in enumerate(incorrectAnswersEn):
            answers.append(
                {
                    "key": f"incorrect_{index}",
                    "answerEn": incorrectAnswerEn,
                    "answerVi": await self.translateAnswerToVietnamese(incorrectAnswerEn),
                    "isCorrect": False,
                }
            )

        if questionType == "boolean":
            answers = self.buildBooleanAnswers(correctAnswerEn)
        else:
            random.shuffle(answers)

        return {
            "id": str(uuid.uuid4()),
            "type": questionType,
            "difficulty": difficulty,
            "categoryEn": categoryEn,
            "questionEn": questionEn,
            "questionVi": questionVi,
            "correctAnswerEn": correctAnswerEn,
            "correctAnswerVi": correctAnswerVi,
            "answers": answers,
        }

    def buildBooleanAnswers(self, correctAnswerEn: str):
        correctAnswer = correctAnswerEn.lower() == "true"

        return [
            {
                "key": "true",
                "answerEn": "True",
                "answerVi": "Đúng",
                "isCorrect": correctAnswer is True,
            },
            {
                "key": "false",
                "answerEn": "False",
                "answerVi": "Sai",
                "isCorrect": correctAnswer is False,
            },
        ]

    def buildQuestionEmbed(self, questionData: dict):
        embed = discord.Embed(title="Câu hỏi mới")
        embed.add_field(
            name="Độ khó",
            value=self.formatDifficulty(questionData["difficulty"]),
            inline=True,
        )
        embed.add_field(
            name="Chủ đề",
            value=questionData["categoryEn"],
            inline=True,
        )
        embed.add_field(
            name="Nội dung câu hỏi",
            value=questionData["questionVi"] or questionData["questionEn"],
            inline=False,
        )

        return embed

    async def answerQuestion(self, questionId: str, answerKey: str, userId: int):
        async with self.questionLock:
            if self.currentQuestion is None or self.currentQuestion["id"] != questionId:
                return {
                    "success": False,
                    "message": "Câu hỏi này đã hết hạn.",
                }

            if self.currentQuestion.get("isProcessing"):
                return {
                    "success": False,
                    "message": "Câu hỏi này đang được xử lý.",
                }

            selectedAnswer = None
            for answer in self.currentQuestion["answers"]:
                if answer["key"] == answerKey:
                    selectedAnswer = answer
                    break

            if selectedAnswer is None:
                return {
                    "success": False,
                    "message": "Câu trả lời không hợp lệ.",
                }

            questionData = self.currentQuestion
            self.currentQuestion["isProcessing"] = True

        if selectedAnswer["isCorrect"]:
            try:
                self.createAnswerHistory(userId, questionData["difficulty"])
            except Exception as e:
                print(f"Quiz answer history create failed: {e}")

                async with self.questionLock:
                    if self.currentQuestion is not None and self.currentQuestion["id"] == questionId:
                        self.currentQuestion["isProcessing"] = False

                return {
                    "success": False,
                    "message": "Không thể ghi lịch sử trả lời câu hỏi.",
                }

        async with self.questionLock:
            if self.currentQuestion is not None and self.currentQuestion["id"] == questionId:
                self.currentQuestion = None

        return {
            "success": True,
            "isCorrect": selectedAnswer["isCorrect"],
            "correctAnswerVi": questionData["correctAnswerVi"],
            "correctAnswerEn": questionData["correctAnswerEn"],
        }

    def createAnswerHistory(self, userId: int, difficulty: str):
        with getDbSession() as session:
            quizAnswerHistoryRepository = QuizAnswerHistoryRepository(session)
            quizAnswerHistoryRepository.create(userId, difficulty)
            session.commit()

    async def translateAnswerToVietnamese(self, text: str):
        if text.lower() == "true":
            return "Đúng"

        if text.lower() == "false":
            return "Sai"

        return await self.translateToVietnamese(text)

    async def translateToVietnamese(self, text: str):
        if not text:
            return text

        try:
            translated = self.translator.translate(text, src="en", dest="vi")
            if inspect.isawaitable(translated):
                translated = await translated

            return translated.text
        except Exception as e:
            print(f"Quiz translation failed: {e}")
            return text

    def formatDifficulty(self, difficulty: str):
        difficultyMap = {
            "easy": "Dễ",
            "medium": "Trung bình",
            "hard": "Khó",
        }

        return difficultyMap.get(difficulty, difficulty)


quizQuestionService = QuizQuestionService()
