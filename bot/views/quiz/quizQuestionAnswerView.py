import traceback

import discord

from bot.services.quiz.quizQuestionService import quizQuestionService


class QuizQuestionAnswerView(discord.ui.View):
    def __init__(self, questionId: str, answers: list[dict]):
        super().__init__(timeout=None)
        self.questionId = questionId

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
        )

        if not result["success"]:
            await interaction.response.send_message(
                result["message"],
                ephemeral=True,
            )
            return

        self.disableViewButtons()
        await interaction.message.edit(view=self.view)

        if result["isCorrect"]:
            await interaction.response.send_message(
                f"Chúc mừng {interaction.user.mention} đã trả lời đúng.",
            )
        else:
            correctAnswer = result["correctAnswerVi"] or result["correctAnswerEn"]
            await interaction.response.send_message(
                f"{interaction.user.mention} bạn đã trả lời sai, câu trả lời đúng là **{correctAnswer}**.",
            )

        await quizQuestionService.sendNextQuestion(interaction.client)

    def disableViewButtons(self):
        if self.view is None:
            return

        for item in self.view.children:
            item.disabled = True

    def formatLabel(self, label: str):
        if len(label) <= 80:
            return label

        return label[:77] + "..."
