from datetime import datetime, timedelta, timezone

import discord

from bot.config.channel import NOTIFICATION_CHANNEL_ID
from bot.config.database import getDbSession
from bot.config.roles import TOP_CHAT_REWARD_ROLES
from bot.repository.memberDailyActivityRepository import MemberDailyActivityRepository
from bot.services.memberActivity.memberChatRankingImageService import MemberChatRankingImageService
from bot.services.memberActivity.memberVoiceRankingImageService import MemberVoiceRankingImageService


class MonthlyTopChatRewardService:
    def __init__(self, bot):
        self.bot = bot
        self.gmt7 = timezone(timedelta(hours=7))
        self.memberChatRankingImageService = MemberChatRankingImageService(bot)
        self.memberVoiceRankingImageService = MemberVoiceRankingImageService(bot)

    async def runMonthlyReward(self):
        channel = self.bot.get_channel(NOTIFICATION_CHANNEL_ID)

        if channel is None:
            channel = await self.bot.fetch_channel(NOTIFICATION_CHANNEL_ID)

        if channel is None:
            return

        guild = channel.guild

        if guild is None:
            return

        nowGmt7 = datetime.now(self.gmt7)
        targetYear = nowGmt7.year
        targetMonth = nowGmt7.month

        with getDbSession() as session:
            memberDailyActivityRepository = MemberDailyActivityRepository(session)

            topChatMembers = memberDailyActivityRepository.findTopLevelChatMembersByMonth(
                targetYear,
                targetMonth,
                50,
            )

            topVoiceMembers = memberDailyActivityRepository.findTopVoiceMembersByMonth(
                targetYear,
                targetMonth,
                10,
            )

        await self.removeOldRewardRoles(guild)
        await self.assignTopChatRewardRoles(guild, topChatMembers)

        chatImageBuffer = await self.memberChatRankingImageService.buildRankingImage(
            topChatMembers[:10],
            guild,
        )

        voiceImageBuffer = await self.memberVoiceRankingImageService.buildRankingImage(
            topVoiceMembers,
            guild,
        )

        chatFile = discord.File(
            fp=chatImageBuffer,
            filename="monthly_chat_ranking.png",
        )

        voiceFile = discord.File(
            fp=voiceImageBuffer,
            filename="monthly_voice_ranking.png",
        )

        await channel.send(
            content=(
                f"## Tổng kết bảng xếp hạng tháng {targetMonth}/{targetYear}\n"
                f"Đã cập nhật role thưởng cho bảng xếp hạng chat tháng này.\n\n"
                f"Top 1 nhận role <@&{TOP_CHAT_REWARD_ROLES['top_1']}>\n"
                f"Top 2 - 10 nhận role <@&{TOP_CHAT_REWARD_ROLES['top_10']}>\n"
                f"Top 11 - 20 nhận role <@&{TOP_CHAT_REWARD_ROLES['top_11_20']}>\n"
                f"Top 21 - 30 nhận role <@&{TOP_CHAT_REWARD_ROLES['top_21_30']}>\n"
                f"Top 31 - 50 nhận role <@&{TOP_CHAT_REWARD_ROLES['top_31_50']}>"
            ),
            files=[
                chatFile,
                voiceFile,
            ],
        )

    async def removeOldRewardRoles(self, guild):
        roleIds = TOP_CHAT_REWARD_ROLES.values()

        for roleId in roleIds:
            role = guild.get_role(roleId)

            if role is None:
                continue

            for member in list(role.members):
                try:
                    await member.remove_roles(
                        role,
                        reason="Reset monthly top chat reward roles",
                    )
                except discord.Forbidden:
                    print(f"Không có quyền remove role {role.name} khỏi {member}")
                except discord.HTTPException as e:
                    print(f"Lỗi khi remove role {role.name} khỏi {member}: {e}")

    async def assignTopChatRewardRoles(self, guild, topChatMembers):
        for index, topMember in enumerate(topChatMembers):
            rank = index + 1
            roleId = self.getRewardRoleIdByRank(rank)

            if roleId is None:
                continue

            role = guild.get_role(roleId)

            if role is None:
                continue

            guildMember = guild.get_member(topMember.user_id)

            if guildMember is None:
                try:
                    guildMember = await guild.fetch_member(topMember.user_id)
                except discord.NotFound:
                    guildMember = None
                except discord.HTTPException:
                    guildMember = None

            if guildMember is None:
                continue

            try:
                await guildMember.add_roles(
                    role,
                    reason=f"Monthly top chat reward rank {rank}",
                )
            except discord.Forbidden:
                print(f"Không có quyền add role {role.name} cho {guildMember}")
            except discord.HTTPException as e:
                print(f"Lỗi khi add role {role.name} cho {guildMember}: {e}")

    def getRewardRoleIdByRank(self, rank):
        if rank == 1:
            return TOP_CHAT_REWARD_ROLES["top_1"]

        if 2 <= rank <= 10:
            return TOP_CHAT_REWARD_ROLES["top_10"]

        if 11 <= rank <= 20:
            return TOP_CHAT_REWARD_ROLES["top_11_20"]

        if 21 <= rank <= 30:
            return TOP_CHAT_REWARD_ROLES["top_21_30"]

        if 31 <= rank <= 50:
            return TOP_CHAT_REWARD_ROLES["top_31_50"]

        return None