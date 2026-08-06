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

    @commands.command(name="topq")
    async def topQuiz(self, ctx, month: int | None = None):
        if ctx.guild is None:
            await ctx.reply("Lệnh này chỉ dùng được trong server.", mention_author=False)
            return

        from datetime import datetime, timezone, timedelta
        gmt7 = timezone(timedelta(hours=7))
        nowGmt7 = datetime.now(gmt7)

        targetYear = nowGmt7.year
        targetMonth = month if month is not None else nowGmt7.month

        if targetMonth < 1 or targetMonth > 12:
            await ctx.reply("Tháng không hợp lệ. Hãy nhập từ 1 đến 12.", mention_author=False)
            return

        from bot.config.database import getDbSession
        from bot.repository.quizAnswerHistoryRepository import QuizAnswerHistoryRepository
        from bot.services.quiz.memberQuizRankingImageService import MemberQuizRankingImageService
        import discord

        with getDbSession() as session:
            quizAnswerHistoryRepository = QuizAnswerHistoryRepository(session)
            topMembers = quizAnswerHistoryRepository.findTopQuizMembersByMonth(
                targetYear,
                targetMonth,
                10,
            )

        imageService = MemberQuizRankingImageService(self.bot)
        imageBuffer = await imageService.buildRankingImage(
            topMembers,
            ctx.guild,
        )

        file = discord.File(
            fp=imageBuffer,
            filename="quiz_ranking.png",
        )

        await ctx.reply(
            content=f"Bảng xếp hạng Quiz tháng **{targetMonth}/{targetYear}**",
            file=file,
            mention_author=False,
        )


async def setup(bot):
    await bot.add_cog(Quiz(bot))
