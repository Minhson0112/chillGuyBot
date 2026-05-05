from discord.ext import commands

from bot.config.database import getDbSession
from bot.repository.farmRepository import FarmRepository
from bot.repository.memberRepository import MemberRepository
from bot.services.farm.farmInitializeService import FarmInitializeService


class CreateFarm(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.farmInitializeService = FarmInitializeService()

    @commands.command(name="createfarm")
    async def createFarm(self, ctx):
        try:
            if ctx.author.bot:
                return

            with getDbSession() as session:
                memberRepository = MemberRepository(session)
                farmRepository = FarmRepository(session)

                member = memberRepository.findByUserId(ctx.author.id)

                if member is None:
                    await ctx.reply("Không tìm thấy dữ liệu member của bạn. Hãy liên hệ quản trị viên.")
                    return

                existingFarm = farmRepository.findByUserId(ctx.author.id)

                if existingFarm is not None:
                    self.farmInitializeService.initializeFarmForMember(
                        session=session,
                        userId=ctx.author.id,
                        isBot=ctx.author.bot,
                    )

                    session.commit()

                    await ctx.reply("Bạn đã có nông trại rồi. Mình đã kiểm tra và bổ sung dữ liệu farm còn thiếu nếu có.")
                    return

                self.farmInitializeService.initializeFarmForMember(
                    session=session,
                    userId=ctx.author.id,
                    isBot=ctx.author.bot,
                )

                session.commit()

            await ctx.reply("Tạo nông trại thành công. Dùng `cg myfarm` để xem farm của bạn.")

        except Exception as e:
            print(f"Create farm error: {e}")
            await ctx.reply("Đã xảy ra lỗi khi tạo nông trại.")


async def setup(bot):
    await bot.add_cog(CreateFarm(bot))