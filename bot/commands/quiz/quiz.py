from discord.ext import commands

from bot.services.quiz.quizQuestionService import quizQuestionService


class Quiz(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="quiz")
    async def restartQuiz(self, ctx: commands.Context):
        if ctx.guild is None:
            await ctx.reply(
                "Lệnh này chỉ dùng được trong server.",
                mention_author=False,
            )
            return

        questionData = await quizQuestionService.resetAndSendQuestion(self.bot)
        if questionData is None:
            await ctx.reply(
                "Không thể tạo câu hỏi mới.",
                mention_author=False,
            )
            return

        await ctx.reply(
            "Đã xoá câu hỏi cũ và gửi câu hỏi quiz mới.",
            mention_author=False,
        )


async def setup(bot):
    await bot.add_cog(Quiz(bot))
