import discord

from bot.config.channel import TICKET_CHANNEL_ID
from bot.config.database import getDbSession
from bot.config.decoration import FOOTER_DECORATION_IMG_URL
from bot.config.emoji import JOIN_BUTTON, WING_L, WING_R
from bot.enums.giveawayStatus import GiveawayStatus
from bot.enums.giveawayType import GiveawayType
from bot.helper.numberFormatHelper import formatNumber
from bot.repository.giveawayParticipantRepository import GiveawayParticipantRepository
from bot.repository.giveawayRepository import GiveawayRepository
from bot.helper.discordTimestampHelper import (
    formatRelativeTime,
    formatShortTime,
    normalizeDatetime,
)


class GiveawayMessageService:
    def buildGiveawayEmbed(
        self,
        giveaway,
        guild: discord.Guild,
        participantCount: int,
    ):
        guildIconUrl = self.resolveGuildIconUrl(guild)
        embed = discord.Embed(
            title=f"{WING_L} {giveaway.title} {WING_R}",
            description=(
                f"- Tổ chức bởi: <@{giveaway.created_by_user_id}>\n"
                f"- Phần thưởng: {self.buildRewardText(giveaway)}\n"
                f"- Quay thưởng⏰: {formatShortTime(giveaway.draw_at)}, "
                f"{formatRelativeTime(giveaway.draw_at)}\n"
                f"- Số người tham gia: **{participantCount}**"
            ),
            color=discord.Color.gold(),
        )

        if guildIconUrl is None:
            embed.set_author(name="Chill Station Giveaway")
        else:
            embed.set_author(
                name="Chill Station Giveaway",
                icon_url=guildIconUrl,
            )
            embed.set_thumbnail(url=guildIconUrl)

        embed.set_image(url=FOOTER_DECORATION_IMG_URL)
        embed.timestamp = self.resolveEmbedTimestamp(giveaway.draw_at)
        embed.set_footer(text=f"Số người thắng: {giveaway.winner_count}")

        return embed

    def buildRewardText(self, giveaway):
        rewardEmoji = self.resolveRewardEmoji(giveaway.type)
        rewardUnit = self.resolveRewardUnit(giveaway.type)

        giveawayType = GiveawayType(giveaway.type)

        if giveawayType.isSubscription:
            return f"{rewardEmoji} **{giveaway.reward_text}** {rewardUnit}"

        if giveaway.type == GiveawayType.CUSTOM.value:
            return giveaway.reward_text or "Custom"

        rewardAmount = self.resolveRewardAmount(giveaway)
        return f"{rewardEmoji} **{formatNumber(rewardAmount)}** {rewardUnit}"

    def resolveRewardEmoji(self, giveawayType: str):
        return GiveawayType(giveawayType).emoji

    def resolveRewardUnit(self, giveawayType: str):
        return GiveawayType(giveawayType).unit

    def resolveRewardAmount(self, giveaway):
        if giveaway.type == GiveawayType.CHILL_COIN.value:
            return giveaway.reward_chill_coin

        if giveaway.type == GiveawayType.COWONCY.value:
            return giveaway.reward_cowoncy

        if giveaway.type == GiveawayType.VND.value:
            return giveaway.reward_vnd

        return None

    def resolveGuildIconUrl(self, guild: discord.Guild):
        if guild.icon is None:
            return None

        return guild.icon.url

    def resolveEmbedTimestamp(self, value):
        return normalizeDatetime(value)

    def buildGiveawayEmbedById(self, giveawayId: int, guild: discord.Guild):
        with getDbSession() as session:
            giveawayRepository = GiveawayRepository(session)
            participantRepository = GiveawayParticipantRepository(session)
            giveaway = giveawayRepository.findById(giveawayId)

            if giveaway is None:
                return None

            participantCount = participantRepository.countActiveParticipants(giveawayId)

            return self.buildGiveawayEmbed(
                giveaway=giveaway,
                guild=guild,
                participantCount=participantCount,
            )

    def joinGiveaway(self, giveawayId: int, userId: int, userRoleIds: list[int]):
        with getDbSession() as session:
            giveawayRepository = GiveawayRepository(session)
            participantRepository = GiveawayParticipantRepository(session)
            giveaway = giveawayRepository.findById(giveawayId)

            if giveaway is None:
                return {
                    "success": False,
                    "message": "Giveaway không tồn tại.",
                }

            if giveaway.status != GiveawayStatus.ACTIVE.value:
                return {
                    "success": False,
                    "message": "Giveaway này không còn hoạt động.",
                }

            if giveaway.limit_role_id is not None and giveaway.limit_role_id not in userRoleIds:
                return {
                    "success": False,
                    "message": (
                        f"Giveaway này yêu cầu role <@&{giveaway.limit_role_id}>, "
                        f"nếu bạn không biết cách lấy role này có thể <#{TICKET_CHANNEL_ID}> chúng tớ sẽ giải đáp."
                    ),
                }

            existingParticipant = participantRepository.findByGiveawayIdAndUserId(
                giveawayId=giveawayId,
                userId=userId,
            )

            if existingParticipant is not None:
                return {
                    "success": True,
                    "alreadyJoined": True,
                    "message": "Bạn đã tham gia giveaway này rồi.",
                }

            participantRepository.create(
                giveawayId=giveawayId,
                userId=userId,
            )
            participantCount = participantRepository.countActiveParticipants(giveawayId)
            session.commit()

            return {
                "success": True,
                "alreadyJoined": False,
                "message": "Bạn đã tham gia giveaway thành công.",
                "participantCount": participantCount,
            }

    def findActiveParticipants(self, giveawayId: int):
        with getDbSession() as session:
            participantRepository = GiveawayParticipantRepository(session)
            participants = participantRepository.findActiveParticipantsByGiveawayId(giveawayId)

            return [
                {
                    "userId": participant.user_id,
                    "joinedAt": participant.joined_at,
                }
                for participant in participants
            ]
