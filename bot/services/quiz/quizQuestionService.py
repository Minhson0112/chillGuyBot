import asyncio
import json
import random
import re
from sqlalchemy import text
import discord

from bot.config.channel import QUESTION_CHANNEL_ID
from bot.config.database import getDbSession
from bot.repository.quizAnswerHistoryRepository import QuizAnswerHistoryRepository


class QuizQuestionService:
    def __init__(self):
        self.recent_question_ids = []
        self.currentQuestion = None
        self.answers_submitted = {}  # user_id -> (submitted_value, is_correct, display_name)
        self.countdown_task = None
        self.questionLock = asyncio.Lock()
        self.hasStarted = False
        self.active_view = None
        self.current_channel = None

    async def startOnReady(self, bot):
        if self.hasStarted:
            return

        self.hasStarted = True
        
        # Wait up to 10 seconds for the Discord client guild/channel cache to populate
        for _ in range(5):
            if bot.guilds:
                break
            await asyncio.sleep(2)

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

        from bot.views.quiz.quizQuestionAnswerView import QuizQuestionAnswerView
        if questionData["type"] == "fill_in":
            view = QuizQuestionAnswerView(questionData["id"], [], is_fill_in=True)
            self.active_view = view
            await channel.send(embed=embed, view=view)
        else:
            view = QuizQuestionAnswerView(questionData["id"], questionData["answers"])
            self.active_view = view
            await channel.send(embed=embed, view=view)

        return questionData

    def get_random_question(self):
        try:
            with getDbSession() as session:
                if self.recent_question_ids:
                    ids_str = ", ".join(f"'{qid}'" for qid in self.recent_question_ids)
                    sql = f"SELECT id, question, type, difficulty, options, correct_answer FROM quiz_questions WHERE id NOT IN ({ids_str}) ORDER BY RAND() LIMIT 1"
                else:
                    sql = "SELECT id, question, type, difficulty, options, correct_answer FROM quiz_questions ORDER BY RAND() LIMIT 1"
                
                row = session.execute(text(sql)).fetchone()
                
                # Fallback if no questions left in current rotation
                if not row and self.recent_question_ids:
                    self.recent_question_ids = []
                    sql = "SELECT id, question, type, difficulty, options, correct_answer FROM quiz_questions ORDER BY RAND() LIMIT 1"
                    row = session.execute(text(sql)).fetchone()
        except Exception as e:
            print(f"Error fetching question from DB: {e}")
            return None

        if not row:
            return None

        q_id, question_text, db_type, difficulty, options_json, correct_answer = row
        self.recent_question_ids.append(q_id)
        if len(self.recent_question_ids) > 100:
            self.recent_question_ids.pop(0)

        # Parse options list
        try:
            options = json.loads(options_json)
        except Exception:
            options = []

        if not options:
            options = [correct_answer]

        # Dynamically determine the question type at runtime:
        # 50% multiple_choice, 25% boolean, 25% fill_in
        rand = random.random()
        if rand < 0.50:
            q_type = "multiple_choice"
            answers = []
            for idx, opt in enumerate(options):
                answers.append({
                    "key": f"opt_{idx}",
                    "answerVi": opt,
                    "isCorrect": opt == correct_answer
                })
            random.shuffle(answers)
            
            return {
                "id": q_id,
                "type": q_type,
                "difficulty": difficulty,
                "questionVi": question_text,
                "correctAnswerVi": correct_answer,
                "answers": answers,
            }
        elif rand < 0.75:
            q_type = "boolean"
            is_statement_correct = random.choice([True, False])
            
            if is_statement_correct:
                selected_option = correct_answer
                correct_bool_ans = "Đúng"
            else:
                wrong_options = [o for o in options if o != correct_answer]
                if wrong_options:
                    selected_option = random.choice(wrong_options)
                else:
                    selected_option = "đáp án không chính xác"
                correct_bool_ans = "Sai"
            
            boolean_question_text = f"{question_text}\n\n👉 **Ý kiến:** *'{selected_option}' là Đúng hay Sai?*"
            
            answers = [
                {
                    "key": "true",
                    "answerVi": "Đúng",
                    "isCorrect": correct_bool_ans == "Đúng"
                },
                {
                    "key": "false",
                    "answerVi": "Sai",
                    "isCorrect": correct_bool_ans == "Sai"
                }
            ]
            
            return {
                "id": q_id,
                "type": q_type,
                "difficulty": difficulty,
                "questionVi": boolean_question_text,
                "correctAnswerVi": correct_bool_ans,
                "answers": answers,
            }
        else:
            q_type = "fill_in"
            return {
                "id": q_id,
                "type": q_type,
                "difficulty": difficulty,
                "questionVi": question_text,
                "correctAnswerVi": correct_answer,
                "answers": [],
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
            desc += "\n\n👉 *Hãy nhấn nút **Điền đáp án** bên dưới để gửi câu trả lời của bạn!*"
        
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
            self.answers_submitted[userId] = (selectedAnswer["answerVi"], is_correct, display_name)

            first_answer = len(self.answers_submitted) == 1
            if first_answer:
                self.countdown_task = asyncio.create_task(self.run_countdown(questionId))

        return {
            "success": True,
            "isCorrect": is_correct,
            "countdown_started": first_answer,
        }

    async def answerFillInQuestion(self, questionId: str, user_answer: str, userId: int, display_name: str):
        async with self.questionLock:
            if self.currentQuestion is None or self.currentQuestion["id"] != questionId:
                return {
                    "success": False,
                    "message": "Câu hỏi này đã hết hạn hoặc đang được xử lý.",
                }

            if userId in self.answers_submitted:
                return {
                    "success": False,
                    "message": "Bạn đã gửi đáp án cho câu hỏi này rồi!",
                }

            guess = user_answer.strip().lower()
            correct = self.currentQuestion["correctAnswerVi"].strip().lower()
            
            # Clean symbols or accents if typed differently
            guess = re.sub(r'^[“"\'\s\.]+|[”"\'\s\.]+$', '', guess)
            correct = re.sub(r'^[“"\'\s\.]+|[”"\'\s\.]+$', '', correct)

            is_correct = (guess == correct)
            self.answers_submitted[userId] = (user_answer, is_correct, display_name)

            first_answer = len(self.answers_submitted) == 1
            if first_answer:
                self.countdown_task = asyncio.create_task(self.run_countdown(questionId))

        return {
            "success": True,
            "isCorrect": is_correct,
            "countdown_started": first_answer,
        }

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
            for user_id, (submitted_val, is_correct, name) in answers.items():
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
