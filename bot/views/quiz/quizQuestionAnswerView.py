import traceback
import discord

from bot.services.quiz.quizQuestionService import quizQuestionService


class QuizQuestionAnswerView(discord.ui.View):
    def __init__(self, questionId: str, answers: list[dict], is_fill_in: bool = False):
        super().__init__(timeout=None)
        self.questionId = questionId

        if is_fill_in:
            self.add_item(QuizFillInButton(questionId))
        else:
            for answer in answers:
                self.add_item(QuizQuestionAnswerButton(questionId, answer))

    async def on_error(self, interaction: discord.Interaction, error: Exception, item):
        traceback.print_exception(type(error), error, error.__traceback__)

        if interaction.response.is_done():
            await interaction.followup.send(
                "Đã xảy ra lỗi khi xử lý câu trả lời.",
                ephemeral=True,
            )
            return

        await interaction.response.send_message(
            "Đã xảy ra lỗi khi xử lý câu trả lời.",
            ephemeral=True,
        )


class QuizQuestionAnswerButton(discord.ui.Button):
    def __init__(self, questionId: str, answer: dict):
        super().__init__(
            label=self.formatLabel(answer["answerVi"]),
            style=discord.ButtonStyle.primary,
            custom_id=f"quiz_answer:{questionId}:{answer['key']}",
        )
        self.questionId = questionId
        self.answerKey = answer["key"]

    async def callback(self, interaction: discord.Interaction):
        if interaction.guild is None:
            await interaction.response.send_message(
                "Câu hỏi này chỉ dùng được trong server.",
                ephemeral=True,
            )
            return

        result = await quizQuestionService.answerQuestion(
            self.questionId,
            self.answerKey,
            interaction.user.id,
            interaction.user.display_name,
        )

        if not result["success"]:
            await interaction.response.send_message(
                result["message"],
                ephemeral=True,
            )
            return

        if result["countdown_started"]:
            await interaction.response.send_message(
                "Chúc mừng bạn đã trả lời đầu tiên! Thời gian đếm ngược 10 giây bắt đầu để người khác cùng trả lời.",
                ephemeral=True,
            )
        else:
            await interaction.response.send_message(
                "Đã ghi nhận câu trả lời của bạn! Hãy chờ 10 giây đếm ngược kết thúc.",
                ephemeral=True,
            )

    def disableViewButtons(self):
        if self.view is None:
            return

        for item in self.view.children:
            item.disabled = True

    def formatLabel(self, label: str):
        if len(label) <= 80:
            return label

        return label[:77] + "..."


class QuizFillInModal(discord.ui.Modal, title="Nhập câu trả lời"):
    answer_input = discord.ui.TextInput(
        label="Câu trả lời của bạn",
        placeholder="Nhập đáp án tại đây...",
        required=True,
    )

    def __init__(self, question_id):
        super().__init__()
        self.question_id = question_id

    async def on_submit(self, interaction: discord.Interaction):
        user_answer = self.answer_input.value
        
        result = await quizQuestionService.answerFillInQuestion(
            self.question_id,
            user_answer,
            interaction.user.id,
            interaction.user.display_name
        )

        if not result["success"]:
            await interaction.response.send_message(
                result["message"],
                ephemeral=True,
            )
            return

        if result["countdown_started"]:
            await interaction.response.send_message(
                "Chúc mừng bạn đã trả lời đầu tiên! Thời gian đếm ngược 10 giây bắt đầu để người khác cùng trả lời.",
                ephemeral=True,
            )
        else:
            await interaction.response.send_message(
                "Đã ghi nhận câu trả lời của bạn! Hãy chờ 10 giây đếm ngược kết thúc.",
                ephemeral=True,
            )


class QuizFillInButton(discord.ui.Button):
    def __init__(self, questionId: str):
        super().__init__(
            label="📝 Điền đáp án",
            style=discord.ButtonStyle.success,
            custom_id=f"quiz_fill_in:{questionId}",
        )
        self.questionId = questionId

    async def callback(self, interaction: discord.Interaction):
        modal = QuizFillInModal(self.questionId)
        await interaction.response.send_modal(modal)
