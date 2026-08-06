import asyncio
import json
import os
import random

import discord

from bot.config.channel import QUESTION_CHANNEL_ID
from bot.config.database import getDbSession
from bot.repository.quizAnswerHistoryRepository import QuizAnswerHistoryRepository


class QuizQuestionService:
    def __init__(self):
        self.questions = []
        self.recent_question_ids = []
        self.currentQuestion = None
        self.answers_submitted = {}  # user_id -> (answer_key, is_correct, display_name)
        self.countdown_task = None
        self.questionLock = asyncio.Lock()
        self.hasStarted = False
        self.active_view = None
        self.load_questions()

    def load_questions(self):
        try:
            path = "bot/assets/quiz/vnhsge_questions.json"
            if os.path.exists(path):
                with open(path, "r", encoding="utf-8") as f:
                    self.questions = json.load(f)
                print(f"✅ Loaded {len(self.questions)} local VNHSGE questions")
            else:
                print("❌ Local VNHSGE questions file not found!")
        except Exception as e:
            print(f"Error loading local questions: {e}")

    async def startOnReady(self, bot):
        if self.hasStarted:
            return

        self.hasStarted = True
        await self.sendNextQuestion(bot)

    async def resetAndSendQuestion(self, bot):
        async with self.questionLock:
            if self.countdown_task:
                self.countdown_task.cancel()
                self.countdown_task = None
            self.currentQuestion = None
            self.answers_submitted = {}

        return await self.sendNextQuestion(bot)

    async def sendNextQuestion(self, bot):
        channel = bot.get_channel(QUESTION_CHANNEL_ID)
        if channel is None:
            try:
                channel = await bot.fetch_channel(QUESTION_CHANNEL_ID)
            except Exception:
                print("QUESTION_CHANNEL_ID not found, falling back to first available text channel")
                if bot.guilds:
                    for guild in bot.guilds:
                        for chan in guild.text_channels:
                            channel = chan
                            break
                        if channel:
                            break

        if channel is None:
            print("No text channel found in any guild.")
            return None

        self.current_channel = channel

        questionData = self.get_random_question()
        if questionData is None:
            await channel.send("Không thể tải câu hỏi mới.")
            return None

        async with self.questionLock:
            self.currentQuestion = questionData
            self.answers_submitted = {}
            self.countdown_task = None
            self.active_view = None

        embed = self.buildQuestionEmbed(questionData)

        if questionData["type"] == "fill_in":
            await channel.send(embed=embed)
        else:
            from bot.views.quiz.quizQuestionAnswerView import QuizQuestionAnswerView
            view = QuizQuestionAnswerView(questionData["id"], questionData["answers"])
            self.active_view = view
            await channel.send(embed=embed, view=view)

        return questionData

    def get_random_question(self):
        if not self.questions:
            return None

        available = [q for q in self.questions if q["id"] not in self.recent_question_ids]
        if not available:
            self.recent_question_ids = []
            available = self.questions

        q = random.choice(available)
        self.recent_question_ids.append(q["id"])
        if len(self.recent_question_ids) > 15:
            self.recent_question_ids.pop(0)

        # Structure answers
        answers = []
        if q["type"] == "multiple_choice":
            for idx, opt in enumerate(q["options"]):
                answers.append({
                    "key": f"opt_{idx}",
                    "answerVi": opt,
                    "isCorrect": opt == q["correct_answer"]
                })
            random.shuffle(answers)
        elif q["type"] == "boolean":
            answers = [
                {
                    "key": "true",
                    "answerVi": "Đúng",
                    "isCorrect": q["correct_answer"] == "Đúng"
                },
                {
                    "key": "false",
                    "answerVi": "Sai",
                    "isCorrect": q["correct_answer"] == "Sai"
                }
            ]

        return {
            "id": q["id"],
            "type": q["type"],
            "difficulty": q["difficulty"],
            "questionVi": q["question"],
            "correctAnswerVi": q["correct_answer"],
            "answers": answers,
        }

    def buildQuestionEmbed(self, questionData: dict):
        difficulty_map = {
            "easy": "Dễ",
            "medium": "Trung bình",
            "hard": "Khó",
        }
        type_map = {
            "multiple_choice": "Trắc nghiệm",
            "boolean": "Đúng / Sai",
            "fill_in": "Điền vào chỗ trống",
        }

        embed = discord.Embed(
            title="❓ CÂU HỎI QUIZ MỚI",
            color=discord.Color.blue(),
        )
        embed.add_field(
            name="Độ khó",
            value=difficulty_map.get(questionData["difficulty"], questionData["difficulty"]),
            inline=True,
        )
        embed.add_field(
            name="Loại câu hỏi",
            value=type_map.get(questionData["type"], questionData["type"]),
            inline=True,
        )
        
        desc = questionData["questionVi"]
        if questionData["type"] == "fill_in":
            desc += "\n\n👉 *Hãy gõ câu trả lời của bạn trực tiếp vào kênh chat này!*"
        
        embed.description = desc
        return embed

    async def answerQuestion(self, questionId: str, answerKey: str, userId: int, display_name: str):
        async with self.questionLock:
            if self.currentQuestion is None or self.currentQuestion["id"] != questionId:
                return {
                    "success": False,
                    "message": "Câu hỏi này đã hết hạn hoặc đang được xử lý.",
                }

            if userId in self.answers_submitted:
                return {
                    "success": False,
                    "message": "Bạn đã chọn đáp án cho câu hỏi này rồi!",
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

            is_correct = selectedAnswer["isCorrect"]
            self.answers_submitted[userId] = (answerKey, is_correct, display_name)

            first_answer = len(self.answers_submitted) == 1
            if first_answer:
                self.countdown_task = asyncio.create_task(self.run_countdown(questionId))

        return {
            "success": True,
            "isCorrect": is_correct,
            "countdown_started": first_answer,
        }

    async def checkFillInAnswer(self, message: discord.Message):
        async with self.questionLock:
            if self.currentQuestion is None or self.currentQuestion["type"] != "fill_in":
                return

            user_id = message.author.id
            if user_id in self.answers_submitted:
                return

            guess = message.content.strip().lower()
            correct = self.currentQuestion["correctAnswerVi"].strip().lower()
            
            is_correct = (guess == correct)
            self.answers_submitted[user_id] = (guess, is_correct, message.author.display_name)

            if is_correct:
                await message.add_reaction("✅")
            else:
                await message.add_reaction("❌")

            first_answer = len(self.answers_submitted) == 1
            if first_answer:
                from bot.main import bot as global_bot
                self.countdown_task = asyncio.create_task(self.run_countdown_with_bot(global_bot, self.currentQuestion["id"]))

    async def run_countdown_with_bot(self, bot, question_id):
        await asyncio.sleep(10)
        await self.end_question(bot, question_id)

    async def run_countdown(self, question_id):
        await asyncio.sleep(10)
        from bot.main import bot as global_bot
        await self.end_question(global_bot, question_id)

    async def end_question(self, bot, question_id):
        async with self.questionLock:
            if self.currentQuestion is None or self.currentQuestion["id"] != question_id:
                return

            questionData = self.currentQuestion
            answers = self.answers_submitted.copy()
            self.currentQuestion = None
            self.answers_submitted = {}
            self.countdown_task = None

        if self.active_view:
            try:
                for child in self.active_view.children:
                    child.disabled = True
                channel = self.current_channel
                async for msg in channel.history(limit=5):
                    if msg.author == bot.user and msg.embeds and msg.embeds[0].title == "❓ CÂU HỎI QUIZ MỚI":
                        await msg.edit(view=self.active_view)
                        break
            except Exception as e:
                print(f"Error disabling view buttons: {e}")

        correct_users = []
        incorrect_users = []

        with getDbSession() as db_session:
            quiz_repo = QuizAnswerHistoryRepository(db_session)
            for user_id, (key, is_correct, name) in answers.items():
                if is_correct:
                    correct_users.append(name)
                    try:
                        quiz_repo.create(user_id, questionData["difficulty"])
                    except Exception as e:
                        print(f"Error creating quiz history: {e}")
                else:
                    incorrect_users.append(name)
            db_session.commit()

        embed = discord.Embed(
            title="🏁 TỔNG KẾT CÂU HỎI QUIZ",
            color=discord.Color.gold(),
        )
        embed.description = f"**Câu hỏi:** {questionData['questionVi']}\n**Đáp án đúng:** **{questionData['correctAnswerVi']}**"

        if correct_users:
            embed.add_field(
                name="✅ Trả lời ĐÚNG",
                value=", ".join(correct_users),
                inline=False,
            )
        else:
            embed.add_field(
                name="✅ Trả lời ĐÚNG",
                value="*Không có ai*",
                inline=False,
            )

        if incorrect_users:
            embed.add_field(
                name="❌ Trả lời SAI",
                value=", ".join(incorrect_users),
                inline=False,
            )

        channel = self.current_channel
        await channel.send(embed=embed)

        await asyncio.sleep(3)
        await self.sendNextQuestion(bot)


quizQuestionService = QuizQuestionService()
