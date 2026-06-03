import discord
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from discord.ext import commands

from bot.config.channel import BOT_NOTIFICATION_CHANNEL_ID, SHOP_ROLE_CHANNEL_ID
from bot.services.roleShop.roleShopExpireService import RoleShopExpireService


class RoleShopExpireTask(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.roleShopExpireService = RoleShopExpireService()
        self.scheduler = AsyncIOScheduler(timezone="Asia/Ho_Chi_Minh")

        self.scheduler.add_job(
            self.runExpiredRoleJob,
            CronTrigger(
                hour="2,8,14,20",
                minute=0,
                second=0,
                timezone="Asia/Ho_Chi_Minh",
            ),
            id="roleShopExpireJob",
            replace_existing=True,
        )

        self.scheduler.start()

    async def runExpiredRoleJob(self):
        expiredPurchases = self.roleShopExpireService.findExpiredPurchases()

        if len(expiredPurchases) == 0:
            return

        notificationChannel = await self.resolveNotificationChannel()

        if notificationChannel is None:
            return

        for expiredPurchase in expiredPurchases:
            await self.handleExpiredPurchase(
                notificationChannel=notificationChannel,
                expiredPurchase=expiredPurchase,
            )

    async def handleExpiredPurchase(
        self,
        notificationChannel: discord.TextChannel,
        expiredPurchase: dict,
    ):
        guild = notificationChannel.guild

        member = await self.resolveGuildMember(
            guild=guild,
            userId=expiredPurchase["userId"],
        )

        role = guild.get_role(expiredPurchase["roleId"])

        if member is not None and role is not None:
            if role in member.roles:
                try:
                    await member.remove_roles(
                        role,
                        reason="Role shop expired",
                    )
                except discord.Forbidden:
                    await notificationChannel.send(
                        embed=self.buildRemoveRoleFailedEmbed(
                            member=member,
                            role=role,
                            reason="Bot không có quyền gỡ role này. Vui lòng kiểm tra lại vị trí role của bot.",
                        ),
                        allowed_mentions=discord.AllowedMentions(
                            users=True,
                            roles=False,
                            everyone=False,
                        ),
                    )
                    return
                except discord.HTTPException:
                    await notificationChannel.send(
                        embed=self.buildRemoveRoleFailedEmbed(
                            member=member,
                            role=role,
                            reason="Bot gỡ role thất bại do lỗi Discord. Vui lòng kiểm tra thủ công.",
                        ),
                        allowed_mentions=discord.AllowedMentions(
                            users=True,
                            roles=False,
                            everyone=False,
                        ),
                    )
                    return

        markResult = self.roleShopExpireService.markExpired(
            memberRolePurchaseId=expiredPurchase["id"],
        )

        if not markResult["success"]:
            if member is not None:
                await notificationChannel.send(
                    embed=self.buildMarkExpiredFailedEmbed(
                        member=member,
                        role=role,
                        message=markResult["message"],
                    ),
                    allowed_mentions=discord.AllowedMentions(
                        users=True,
                        roles=False,
                        everyone=False,
                    ),
                )
            return

        if member is None:
            return

        await notificationChannel.send(
            content=member.mention,
            embed=self.buildRoleExpiredEmbed(
                member=member,
                role=role,
                expiredAt=expiredPurchase["expiredAt"],
            ),
            allowed_mentions=discord.AllowedMentions(
                users=True,
                roles=False,
                everyone=False,
            ),
        )

    async def resolveNotificationChannel(self):
        channel = self.bot.get_channel(BOT_NOTIFICATION_CHANNEL_ID)

        if channel is not None:
            return channel

        try:
            channel = await self.bot.fetch_channel(BOT_NOTIFICATION_CHANNEL_ID)
        except discord.NotFound:
            return None
        except discord.Forbidden:
            return None
        except discord.HTTPException:
            return None

        if not isinstance(channel, discord.TextChannel):
            return None

        return channel

    async def resolveGuildMember(
        self,
        guild: discord.Guild,
        userId: int,
    ):
        member = guild.get_member(userId)

        if member is not None:
            return member

        try:
            return await guild.fetch_member(userId)
        except discord.NotFound:
            return None
        except discord.HTTPException:
            return None

    def buildRoleExpiredEmbed(
        self,
        member: discord.Member,
        role: discord.Role | None,
        expiredAt,
    ):
        expiredAtText = expiredAt.strftime("%d/%m/%Y %H:%M")

        roleText = "`Role không còn tồn tại trong server.`"

        if role is not None:
            roleText = role.mention

        embed = discord.Embed(
            title="Role đã hết hạn",
            description=(
                f"Role của bạn đã hết hạn sử dụng.\n\n"
                f"Role: {roleText}\n"
                f"Thời điểm hết hạn: **{expiredAtText}**\n\n"
                f"Nếu muốn tiếp tục sử dụng, hãy mua lại tại kênh <#{SHOP_ROLE_CHANNEL_ID}>."
            ),
            color=discord.Color.orange(),
        )

        embed.set_author(
            name=member.display_name,
            icon_url=member.display_avatar.url,
        )

        return embed

    def buildRemoveRoleFailedEmbed(
        self,
        member: discord.Member,
        role: discord.Role,
        reason: str,
    ):
        embed = discord.Embed(
            title="Không thể gỡ role đã hết hạn",
            description=(
                f"Member: {member.mention}\n"
                f"Role cần gỡ: {role.mention}\n"
                f"Lý do: {reason}"
            ),
            color=discord.Color.red(),
        )

        return embed

    def buildMarkExpiredFailedEmbed(
        self,
        member: discord.Member,
        role: discord.Role | None,
        message: str,
    ):
        roleText = "`Role không còn tồn tại trong server.`"

        if role is not None:
            roleText = role.mention

        embed = discord.Embed(
            title="Cập nhật trạng thái role thất bại",
            description=(
                f"Member: {member.mention}\n"
                f"Role: {roleText}\n"
                f"Lỗi: {message}"
            ),
            color=discord.Color.red(),
        )

        return embed

    def cog_unload(self):
        if self.scheduler.running:
            self.scheduler.shutdown()


async def setup(bot):
    await bot.add_cog(RoleShopExpireTask(bot))
