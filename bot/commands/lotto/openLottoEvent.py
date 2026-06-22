import discord
from discord.ext import commands

from bot.config.channel import NOTIFICATION_CHANNEL_ID
from bot.config.database import getDbSession
from bot.config.emoji import LOGO
from bot.config.roles import MOD_ROLE_IDS
from bot.enums.lottoEventStatus import LottoEventStatus
from bot.repository.lottoEventRepository import LottoEventRepository
from bot.services.lotto.lottoEventMessageService import LottoEventMessageService
from bot.views.lotto.lottoBuyTicketView import LottoBuyTicketView


class OpenLottoEventCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.lottoEventMessageService = LottoEventMessageService()

    @commands.command(name="openlottoevent")
    async def openLottoEvent(self, ctx: commands.Context, lottoEventId: int = None):
        if ctx.guild is None:
            return

        if lottoEventId is None:
            await ctx.reply(
                f"{LOGO} Cách dùng: `cg openlottoevent <lotto_event_id>`",
                mention_author=False,
            )
            return

        if not self.hasEventPermission(ctx.author):
            await ctx.reply(
                f"{LOGO} Bạn không có quyền sử dụng lệnh này.",
                mention_author=False,
            )
            return

        with getDbSession() as dbSession:
            lottoEventRepository = LottoEventRepository(dbSession)
            lottoEvent = lottoEventRepository.findById(lottoEventId)

        if lottoEvent is None:
            await ctx.reply(
                f"{LOGO} Không tìm thấy event lotto.",
                mention_author=False,
            )
            return

        if not lottoEvent.is_active or lottoEvent.status != LottoEventStatus.OPEN.value:
            await ctx.reply(
                f"{LOGO} Event lotto này hiện không mở bán vé.",
                mention_author=False,
            )
            return

        notificationChannel = await self.resolveNotificationChannel(ctx)

        if notificationChannel is None:
            return

        await notificationChannel.send(
            embed=self.lottoEventMessageService.buildLottoEventEmbed(
                guild=ctx.guild,
                lottoEvent=lottoEvent,
            ),
            view=LottoBuyTicketView(lottoEvent.id),
        )

        await ctx.reply(
            f"{LOGO} Đã gửi lotto event lên kênh <#{NOTIFICATION_CHANNEL_ID}>.",
            mention_author=False,
        )

    def hasEventPermission(self, member):
        if not isinstance(member, discord.Member):
            return False

        memberRoleIds = {role.id for role in member.roles}
        allowedRoleIds = {
            MOD_ROLE_IDS["admin"],
            MOD_ROLE_IDS["owner"],
        }

        return not memberRoleIds.isdisjoint(allowedRoleIds)

    async def resolveNotificationChannel(self, ctx: commands.Context):
        notificationChannel = ctx.guild.get_channel(NOTIFICATION_CHANNEL_ID)

        if notificationChannel is None:
            try:
                notificationChannel = await self.bot.fetch_channel(NOTIFICATION_CHANNEL_ID)
            except discord.NotFound:
                await ctx.reply(
                    f"{LOGO} Không tìm thấy kênh Notification.",
                    mention_author=False,
                )
                return None
            except discord.Forbidden:
                await ctx.reply(
                    f"{LOGO} Bot không có quyền truy cập kênh Notification.",
                    mention_author=False,
                )
                return None
            except discord.HTTPException:
                await ctx.reply(
                    f"{LOGO} Không thể lấy thông tin kênh Notification.",
                    mention_author=False,
                )
                return None

        if not isinstance(notificationChannel, discord.TextChannel):
            await ctx.reply(
                f"{LOGO} Notification channel không phải text channel.",
                mention_author=False,
            )
            return None

        return notificationChannel


async def setup(bot):
    await bot.add_cog(OpenLottoEventCommand(bot))
