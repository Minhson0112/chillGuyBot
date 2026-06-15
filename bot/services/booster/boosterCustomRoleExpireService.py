from datetime import datetime

import discord

from bot.config.channel import BOT_NOTIFICATION_CHANNEL_ID, TICKET_CHANNEL_ID
from bot.config.database import getDbSession
from bot.config.emoji import BOOSTER
from bot.enums.boosterCustomRoleRemovedReason import BoosterCustomRoleRemovedReason
from bot.repository.boosterCustomRoleRepository import BoosterCustomRoleRepository


class BoosterCustomRoleExpireService:
    REMOVE_ROLE_REASON = "Booster expired"

    async def handleBoosterExpired(self, bot, member: discord.Member):
        activeCustomRoles = self.findActiveCustomRoles(member.id)

        if len(activeCustomRoles) == 0:
            return

        notificationChannel = await self.resolveNotificationChannel(bot)

        for customRole in activeCustomRoles:
            role = member.guild.get_role(customRole["roleId"])

            if role is None or role not in member.roles:
                self.markCustomRoleRemoved(customRole["id"])
                continue

            try:
                await member.remove_roles(
                    role,
                    reason=self.REMOVE_ROLE_REASON,
                )
            except discord.Forbidden:
                continue
            except discord.HTTPException:
                continue

            markResult = self.markCustomRoleRemoved(customRole["id"])

            if not markResult["success"]:
                continue

            if notificationChannel is not None:
                await notificationChannel.send(
                    content=f"Xin chào {member.mention}",
                    embed=self.buildBoosterExpiredEmbed(role),
                    allowed_mentions=discord.AllowedMentions(
                        users=True,
                        roles=False,
                        everyone=False,
                    ),
                )

    def findActiveCustomRoles(self, memberId: int):
        with getDbSession() as session:
            boosterCustomRoleRepository = BoosterCustomRoleRepository(session)
            boosterCustomRoles = boosterCustomRoleRepository.findActiveByTargetUserId(memberId)

            return [
                {
                    "id": boosterCustomRole.id,
                    "roleId": boosterCustomRole.role_id,
                }
                for boosterCustomRole in boosterCustomRoles
            ]

    def markCustomRoleRemoved(self, boosterCustomRoleId: int):
        removedAt = datetime.now()

        with getDbSession() as session:
            boosterCustomRoleRepository = BoosterCustomRoleRepository(session)
            boosterCustomRole = boosterCustomRoleRepository.findById(boosterCustomRoleId)

            if boosterCustomRole is None:
                return {
                    "success": False,
                    "message": "Không tìm thấy custom role booster.",
                }

            boosterCustomRoleRepository.markRemoved(
                boosterCustomRole=boosterCustomRole,
                removedReason=BoosterCustomRoleRemovedReason.BOOST_REMOVED.value,
                removedAt=removedAt,
            )

            session.commit()

            return {
                "success": True,
            }

    async def resolveNotificationChannel(self, bot):
        channel = bot.get_channel(BOT_NOTIFICATION_CHANNEL_ID)

        if channel is None:
            try:
                channel = await bot.fetch_channel(BOT_NOTIFICATION_CHANNEL_ID)
            except discord.HTTPException:
                return None

        if not isinstance(channel, discord.TextChannel):
            return None

        return channel

    def buildBoosterExpiredEmbed(self, role: discord.Role):
        return discord.Embed(
            description=(
                f"Trạng thái booster {BOOSTER} của bạn trên Chill Station đã hết hiệu lực, "
                f"chúng tôi xin phép gỡ role custom của bạn {role.mention}, "
                f"để lấy lại hãy boost server và <#{TICKET_CHANNEL_ID}> nhé."
            ),
            color=discord.Color.orange(),
        )
